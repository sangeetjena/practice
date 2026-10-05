# Stock ML platform: architecture and execution plan

Status: the first daily logistic baseline now has database extraction, versioned feature calculation, candidate training, a private serving API, a deployment chart, and a `stock/` caller that persists a model-only daily summary. No trained artifact or live deployment has been verified in this environment. The broader hourly multi-model and final-LLM design below remains planned.

For this first baseline, feature calculation is intentionally in `ML_INFRA/` as requested. Its `/features/{symbol}` endpoint reads existing stock databases; `stock/` calls it and owns all prediction and summary writes. Before adding other model families, define a shared versioned feature contract so training and serving cannot drift.

## 1. Objective and boundaries

Build a reproducible two-project flow: `stock/` ingests licensed market and research data, computes point-in-time features, invokes hosted models, stores each prediction, assembles an hourly per-stock summary, and asks its final LLM for a cited assessment. `ML_INFRA/` uses historical stock outputs, matured outcomes, and human feedback to train and evaluate candidate models, then deploys approved versions for `stock/` to call. Preserve every input, prediction, version, later outcome, feedback item, and cost for critique. No real-money autonomous order execution.

| Project | Owns | Does not own |
| --- | --- | --- |
| `stock/` | Source connectors and ingestion; versioned feature engineering; calling deployed model endpoints; prediction, summary, final LLM, outcome and human-feedback persistence; decision/risk workflow and API | Training model weights or provisioning Kubernetes |
| `ML_INFRA/` | Point-in-time training datasets and labels built from stock outputs; offline training/backtests; experiment tracking; immutable artifacts; approval, model-serving deployment, health, monitoring and rollback | Running the stock prediction workflow, writing stock predictions/summaries, final LLM synthesis, cluster/database provisioning |
| `INFRA/` | Kubernetes cluster, base namespaces/storage/networking, Citus/Postgres, TimescaleDB, optional Redis/Qdrant/Cassandra, secrets delivery and resource budgets | Model semantics, trained weights, feature formulas |

`ML_INFRA` reads stock-owned outputs and feedback with a read-only role, stores only its training/registry metadata and artifacts, and deploys private model-serving workloads into the cluster managed by `INFRA`. The model container images and Helm/Kubernetes workload definitions belong to `ML_INFRA`; cluster prerequisites and any new namespace/storage/secret infrastructure are coordinated through `INFRA`. `stock/` owns the client and its database writes. No second Terraform state manages the same Helm release or namespace.

## 2. Data and workflow topology

```text
Licensed market/news/fundamental/analyst sources
       │
       ▼
stock ingestion: normalize, validate, deduplicate, record available_at
       ├── TimescaleDB: bars and time-series observations
       └── Citus/Postgres: immutable source events/documents and ingest runs
                     │ successful source-window completion
                     ▼
stock feature builder: deterministic, versioned, point-in-time
       │ current feature snapshot
       ▼
stock calls approved model A/B/... endpoints hosted by ML_INFRA
       │ prediction responses
       ▼
stock writes immutable model_predictions in Citus/Postgres
       ▼
stock assembles stock_summary_hourly with evidence references
       ▼ complete/material-event gate
stock final LLM synthesis → final_assessments + telemetry
       ▼
stock decision/risk workflow → paper or approval
       ▼ after horizon
stock objective outcomes + critique + human feedback
       │ historical, point-in-time training export (read-only to ML_INFRA)
       ▼
ML_INFRA dataset/labels → training/evaluation → candidate artifact
                                              ↓ human approval
                                  approved registry + model redeployment
```

The `stock/` ingestion module only collects and stores facts. After an ingestion checkpoint, the separate `stock/` research workflow builds features and invokes deployed predictive endpoints. `ML_INFRA` serves versioned model requests and retrains from later results; it never schedules stock predictions. The final LLM belongs to `stock/`, does not run continuously per tick, and may abstain. Deterministic risk rules remain authoritative.

### Cadence and availability

- Daily OHLCV supports a daily forecast, not a meaningful new prediction every hour. An hourly technical forecast requires a licensed intraday feed, completed hourly bars, exchange calendar, and freshness policy. The present Alpha Vantage adapter gates intraday polling behind an entitlement flag; verify the account plan and rate budget before enabling it.
- Prices/volume can refresh per completed bar; news refreshes on arrival; analyst reports and fundamentals refresh on publication and carry their original publication **and first observed/available** times. A summary may reuse the latest valid fundamental snapshot, but must show its age and source.
- Use UTC in storage and an exchange calendar for session boundaries, holidays, and daylight saving. Set an explicit `as_of`/`cutoff_at` for every model and final assessment.
- An ingestion checkpoint is emitted only after required writes to both existing databases succeed. Because the two databases do not share a transaction, retries and reconciliation must recover partial writes. Stable source IDs and unique keys make ingestion idempotent.

## 3. Contracts and storage

Use **existing databases** initially. TimescaleDB keeps market bars and optionally dense feature time series. In Citus/Postgres `agentdb`, `stock/` owns predictions, summaries, final assessments, outcomes, feedback, workflow runs and evidence references. `ML_INFRA` may use a separate `ml_registry` schema for training runs and model metadata under a separate role; immutable model artifacts live in backed-up object/artifact storage. No new summary database server is needed. Cassandra and Qdrant are optional for later use cases; Redis is a queue/cache aid, not the only record of work or decisions.

### Source-event contract

Every event carries `symbol`, `event_type`, `source`, stable `source_id`, `occurred_at`, `published_at` where applicable, `observed_at`/`available_at`, source revision, license/entitlement, payload hash, and quality status. Reject or quarantine malformed payloads. Keep documents and licensed full text outside wide hourly rows; reference their IDs. Historical data must not be treated as known before it was actually available.

### Model input and output contract

- A stock-owned `FeatureSnapshot` has `snapshot_id`, `symbol`, `cutoff_at`, `feature_version`, ordered feature names/values, units, missingness/freshness flags, source event IDs and versions, and a content hash. `ML_INFRA` trains against exported historical snapshots with that exact version and declares the accepted feature schema in each deployed model. `stock/` computes features for live requests; `ML_INFRA` does not independently redefine them.
- A `ModelSpec` has stable name, task, asset universe, horizon, target definition, feature schema/hash, artifact URI/checksum, training cutoff, code/dependency versions, hyperparameters, evaluation report, and status (`candidate`, `approved`, `retired`). Changes to weights, feature formulas, hyperparameters, or label definitions create a new version.
- A stock-owned `ModelPrediction` has `prediction_id`, `symbol`, `cutoff_at`, model name/version, horizon, target definition, class probabilities or regression output, calibration version, `snapshot_id`, input hash, run/trace ID, status, and creation time. The hosted endpoint returns the output but does **not** write this record. Use an idempotency constraint on `(symbol, cutoff_at, model_version, horizon, feature_snapshot_id)`.
- A stock-owned `FinalAssessment` has its own immutable ID, original input-summary ID/hash, LLM provider/model/version, prompt/agent version, evidence references, each model prediction ID, conclusion, uncertainty, abstention reason if any, horizon, thesis/decision links, token usage, latency, and cost. It never overwrites individual model output.
- A stock-owned `HumanFeedback` has feedback ID, target prediction/summary/assessment ID, reviewer identity and role, recorded time, label/rating, rationale, and revision/retraction history. `ML_INFRA` treats this as review evidence, not ground truth by default. Objective realized outcomes are separately computed after the prediction horizon.

### Hourly summary design

`stock/` creates and maintains a query-friendly `stock_summary_hourly` table or view in Citus/Postgres. Suggested stable fields:

```text
summary_id, symbol, bucket_start_utc, cutoff_at, revision, status,
technical_features_json, fundamental_snapshot_id, news_event_ids,
analyst_report_ids, sector_macro_refs, feature_snapshot_id,
model_prediction_ids, final_assessment_id, data_freshness_json,
source_watermarks_json, input_hash, created_at, supersedes_summary_id
```

`stock/` stores **each model prediction as a row in `model_predictions`**, not as `model1_prediction`, `model2_prediction`, etc. columns. A new model then requires no table migration. The hourly summary references the prediction IDs and may expose a compact JSON projection for dashboards. Keep large articles and reports in source tables with links/IDs. Do not overwrite an earlier summary if late data arrives: append a revision and maintain a `latest_stock_summary_hourly` view. Key rows by symbol, hour, and revision; index symbol/time. Model outputs with different horizons remain distinct.

`stock/` builds the summary from the exact feature snapshot and source watermarks used for inference. `status` moves `building → complete` or `partial/failed`; a partial summary explains missing components. A final LLM invocation requires an explicit completeness policy; missing/stale material evidence can force `abstain` or a reduced-confidence assessment. The final LLM output is **not** the objective ground truth or an order. `ML_INFRA` reads selected historical summaries, outcomes, and feedback later for retraining; it never edits them.

## 4. Feature engineering and training

1. **Dataset scope:** choose a target such as `P(next 5 trading-day adjusted return > 2%)`; define price basis, exchange calendar, market-close cutoff, benchmark, universe and costs before fitting. Start with daily bars. Only add hourly targets after intraday history is available.
2. **Features:** `stock/` defines and computes deterministic returns, SMA/EMA distances, RSI, ATR/volatility, relative volume, sector relative strength, and freshness/missingness. `ML_INFRA` consumes a versioned historical export of those feature snapshots. Use fundamentals/news/analyst signals only when their `available_at <= cutoff_at`; source adapters must provide the evidence and rights to use them. Keep feature formulas and lookback windows versioned in `stock/` and test the train/serve contract against that version.
3. **Labels:** compute from future adjusted prices, then store separately from features. A five-day label requires five later trading sessions and must never be fed into inference.
4. **Validation:** split chronologically across all symbols, apply a horizon-sized gap/embargo around boundaries, tune only on training/validation, reserve an untouched final period, then run walk-forward and market-regime tests. Include delisted names where the chosen data source supports them to reduce survivorship bias.
5. **Baselines:** no-skill/base-rate and simple momentum rules; then logistic regression and a tree model such as XGBoost. Add sequence models only after baselines and enough historical coverage justify them. Calibrate probabilities using validation data, not the untouched test set.
6. **Evaluation:** log sample size, class balance, precision/recall, Brier score/calibration, benchmark-relative returns, drawdown, turnover, fees/slippage, failure by symbol/sector/regime, and uncertainty. Accuracy alone is insufficient.
7. **Artifact:** save the complete preprocessing-and-model pipeline, feature schema, environment lock and manifest with checksum. Use immutable artifact locations and backed-up storage. Loading pickle/joblib artifacts requires a trusted source and compatible library versions; consider `skops` or ONNX when appropriate.

Training runs are resource-limited `ML_INFRA` Kubernetes Jobs with a fixed image and immutable dataset snapshot. A scheduled or explicitly requested retrain reads completed stock summaries, matured objective outcomes, and human feedback through a read-only contract. Feedback can flag false positives, missing evidence, or label disputes; it must be quality-checked and cannot silently rewrite the objective outcome. A new candidate is evaluated against the champion before any deployment. Training never runs inside `stock/` ingestion or its API server. Initial local training may run outside Kubernetes using the same contract.

## 5. Registry, promotion, serving, and rollback

`ML_INFRA` starts with a small registry in an isolated `ml_registry` schema plus immutable artifact files in a backed-up artifact store. The registry records candidate/approved/retired state and a `champion` pointer. Human review checks the evaluation report, leakage gates, data license, resource cost, and comparison with the current champion. Deploy a candidate to a shadow endpoint first; `stock/` may call it for comparison but labels its outputs as shadow and excludes them from decisions. Promotion changes the approved pointer/deployment and records reviewer, time, reason, and old version. Rollback restores the previous deployment; `stock/` prediction records continue to identify the exact version used.

MLflow can replace the minimal registry when experiment comparison and artifact workflows outgrow it. Self-hosted MLflow Model Registry needs a database-backed metadata store; artifact storage is separate. Do not add it to the 16 GB local cluster until its benefit outweighs its footprint. Do not deploy KServe or GPU serving merely to run a few hourly tabular models.

**Serving mode:** `ML_INFRA` deploys a private, authenticated model API inside the INFRA cluster. It loads approved artifacts, validates a `FeatureSnapshot` and schema/version/hash, returns model name/version, horizon, target definition, probability/output, calibration version and request ID, and does not write stock databases. Use health/readiness checks, a pinned artifact checksum, resource limits, and no public ingress. Batch prediction is still possible: `stock/` calls the endpoint with a batch of symbols after ingestion completes. Consider KServe only after this simple endpoint no longer meets measured scale or rollout needs.

`stock/` owns the final LLM synthesis adapter. It calls an approved external model API initially, saves the structured assessment and telemetry, and enforces citation, completeness and abstention rules. Hosting LLM weights locally would require separate compute/GPU sizing and an explicit later decision. Prompt changes follow the stock project's evaluation/approval flow. Technical rules and risk limits are not delegated to the LLM.

## 6. Scheduling and orchestration

- `stock/` ingestion records a durable `ingest_runs`/source-window checkpoint. Its coordinator claims a unique `(symbol, cutoff_at, workflow_version)` work item only after required sources are ready. It calculates features, calls the private model endpoints, writes each response to `model_predictions`, assembles the hourly summary, and runs its final LLM when eligible. Redis can wake workers, but Postgres holds the durable claim and result.
- `ML_INFRA` schedules training/retraining Jobs separately from stock runtime jobs, with resource limits and immutable training snapshots. It publishes a new serving version only after evaluation and approval. A deployment event tells `stock/` which endpoint/version is available; active stock runs pin the exact version they call.
- A Kubernetes CronJob may launch the stock coordinator or ML training, but two unrelated CronJobs scheduled minutes apart are **not** a dependency guarantee. Set `timeZone`, `concurrencyPolicy`, starting deadline and history limits explicitly. The stock coordinator enforces exchange calendars, provider quotas, and readiness checkpoints.
- `stock/` news/material-event triggers use dedupe, cooldown and a minimum-information threshold. A material event may rebuild the current summary before the next hour without retraining the price model.
- At the prediction horizon, a `stock/` outcome worker calculates objective returns and target/stop order using subsequent prices; its critique process distinguishes original reasoning issues from later news. `ML_INFRA` consumes those immutable results and reviewed human feedback at the next retraining cycle without hindsight leakage in historical feature rows.

## 7. Security, telemetry, and operations

- Kubernetes Secrets or an approved secret manager hold source, database, and LLM credentials. Use separate read/write DB roles, TLS where available, network policies, restricted service accounts, and no public model/MLflow/Qdrant/DB endpoints by default.
- `stock/` records ingest, feature, model-call, summary and synthesis run/trace IDs, symbol, cutoff, input/output hashes, versions, latency and errors. Its LLM spans also record provider/model/version, prompt version, input/output/cached/reasoning tokens when exposed, tool calls and estimated USD cost. `ML_INFRA` records training/evaluation, artifact, approval and serving-deployment telemetry. Both sides propagate a correlation ID. Never log API keys or full connection URLs.
- `stock/` monitors data freshness, missing bars, source lag, feature null rates, call errors, LLM cost, queue age and partial summaries. `ML_INFRA` monitors endpoint latency/health, model version, prediction distribution and calibration/drift after labels mature. Alert on source outages and model-feature mismatches.
- Back up database state and artifacts; test restore. Pin container and dependency versions, scan images, and use resource requests/limits. Start with low-memory models on the current cluster; budget capacity before adding another always-on service.
- Keep source data rights, retention, analyst-report licenses and prompt sharing permissions explicit. External text is untrusted and must not be allowed to change instructions or risk rules.

## 8. Phased execution and acceptance gates

### Phase 0 — contracts and data audit

Agree on typed stock-to-model request/response and stock-to-training export contracts; inventory symbols, history length, adjustment policy, provider quotas, licensing, and current INFRA capacity. Verify ingestion round trips on Citus/TimescaleDB and a stable `available_at` rule. **Gate:** no training until target, universe, data rights, and point-in-time policy are written down.

### Phase 1 — deterministic feature and summary foundation

In `stock/`, implement versioned `FeatureSnapshot`, historical feature export, `ingest_runs`, `model_predictions`, `stock_summary_hourly`, `final_assessments`, `human_feedback`, migrations and read queries. `ML_INFRA` implements read-only adapters and contract tests against those exports. Test train/serve feature compatibility, late data revisions, DST/holidays, missing data, and idempotency. **Gate:** replaying the same cutoff produces the same feature hash and summary revision policy.

### Phase 2 — baseline training

In `ML_INFRA`, implement datasets/labels from stock exports and outcomes, chronological walk-forward evaluation, logistic baseline and gradient-boosted candidate, calibration, fees/slippage report, experiment metadata and immutable artifact. Incorporate human feedback only through documented, quality-checked features/labels/weights. **Gate:** untouched-period results and leakage tests reviewed; no claim of predictiveness from training accuracy.

### Phase 3 — registry and model deployment

In `ML_INFRA`, implement approval, champion/shadow pointers, rollback, artifact verification and a private model-serving endpoint. Package a reproducible image and deploy to INFRA's cluster with resource limits and secrets. In `stock/`, implement the endpoint client, version pinning, retry/idempotency and prediction persistence. **Gate:** approved version only, deterministic replay, contract match, rollback drill and artifact restore drill.

### Phase 4 — hourly assembly and final synthesis

In `stock/`, only after licensed intraday data exists: complete hourly bars, feature freshness, individual model calls/outputs, material-event gating, bounded LLM context, structured final assessment, citation validation, token/cost telemetry and abstention. For daily-only data, use a daily summary instead. `ML_INFRA` remains responsible for model-serving health and versions. **Gate:** historical replay proves no post-cutoff evidence entered any original assessment.

### Phase 5 — shadow, paper, and operating review

`stock/` runs shadow calls, saves predictions, compares matured outcomes, captures critique and human feedback, and keeps paper/risk controls. `ML_INFRA` consumes these outputs for measured retraining and redeploys only approved improvements; prompt/rule proposals stay in `stock/`. No real-money autonomous execution. **Gate:** sustained paper results, risk veto tests, human approval path, monitoring and incident runbooks.

## 9. Key implementation decisions to confirm

1. Primary exchange(s), ticker universe, market calendar and whether the initial model is daily or licensed hourly.
2. First target/horizon and adjusted-price/corporate-action policy.
3. Analyst-report source and rights; no reports are currently ingested.
4. Initial artifact store (backed-up local volume versus object storage), model-serving authentication, and whether MLflow is warranted.
5. Maximum model/LLM spend, the stock-owned completeness threshold for an hourly final assessment, and how human feedback is reviewed before use in retraining.

Until those choices are settled, implement contracts and data-quality checks; do not train on the current compact single-symbol sample and present its result as a validated signal.

## Reference documentation

- [Alpha Vantage API documentation](https://www.alphavantage.co/documentation/): compact daily history and entitlement details.
- [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) and [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html): leakage controls and chronological validation.
- [scikit-learn model persistence](https://scikit-learn.org/stable/model_persistence.html): artifact security and environment compatibility.
- [MLflow Model Registry](https://mlflow.org/docs/latest/ml/model-registry/workflow/): versioned artifacts, aliases, and database-backed registry requirement.
- [Kubernetes CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/): time zones, concurrency and possible duplicate/missed runs.
- [KServe](https://kserve.github.io/website/): later serving option if a simple batch worker or private API is insufficient.
