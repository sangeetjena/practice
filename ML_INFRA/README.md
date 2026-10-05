# ML_INFRA

Model training, evaluation, versioning, and deployment for the stock research system.
The first daily logistic training and serving path is implemented but requires existing history, a reviewed artifact, and deployment.
See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the implementation contract and phased plan.

## First model: daily logistic direction

### Automated workflow

Create `ML_INFRA/.env` from `.env.example` with local database URLs, in-cluster database URLs, and a model token. From `ML_INFRA/`:

```bash
make prerequisites
make test
make train SYMBOL=IBM
make deploy
make predict TEST_FILE=tests/predict.json
make status
```

`make prerequisites` creates a separate `ML_INFRA/.venv` if needed and installs this package with serving and test dependencies only when they are missing, inconsistent, or its package configuration has changed. Every `train`, `predict`, `deploy`, and `test` run invokes that prerequisite and activates the same venv; you do not need to activate it manually. It checks package presence and `pip check` before skipping installation. For GPU training, the venv must contain a CUDA-enabled PyTorch build; `make train` fails clearly if CUDA is unavailable.

`make train` trains a GPU-required candidate from TimescaleDB bars and Postgres fundamentals. `make deploy` builds that artifact into an image, loads it into the existing kind cluster, installs one serving replica in `logistic-regression`, and opens `http://127.0.0.1:8000` through a local port forward. `make predict` reads a JSON test snapshot and posts it to `http://127.0.0.1:8000/predict`; it does not store a stock result. Match the test file's symbol to the trained model. Use `python -m stock_research.predict --symbol IBM` from `stock/` when you want to persist a real prediction and summary. The deployment is pinned to the existing `local-platform-worker` node; it does not add a new kind node.

`make deploy` requires `docker`, `kind`, `kubectl`, and `helm` in the same shell as the kind cluster. The local URLs in `.env` are for training; `ML_DATABASE_URL_IN_CLUSTER` and `ML_TIMESCALE_URL_IN_CLUSTER` must use Kubernetes service DNS. URL-encode password characters that are reserved in URLs. The port forward PID and logs are kept in `.state/`. Only use the localhost endpoint for development.

The local kind connection defaults to `ML_DATABASE_SSLMODE=disable` and `ML_TIMESCALE_SSLMODE=disable`. This avoids an unnecessary SSL negotiation through `kubectl port-forward`; use a verified TLS mode when moving to an environment that provides TLS for the databases.

The stock client URL is `http://127.0.0.1:8000` when it runs on the same development host as the port forward. A stock pod in Kubernetes instead uses `http://stock-model.logistic-regression.svc.cluster.local:8000`. Both clients call `GET /features/{symbol}` followed by `POST /predict`; only `stock/` persists the prediction.

The model predicts whether the next completed daily close is higher than the current daily close. There is no transferable pretrained logistic regression artifact for this dataset. PyTorch trains on CUDA when available; `--require-gpu` fails if CUDA is unavailable. The JSON artifact records model version, train/test counts, held-out accuracy, base rate, feature contract, and device. This is a research baseline, not a validated trading signal. Review its held-out metrics before running `make deploy`; deployment of a candidate does not claim investment accuracy.

From `ML_INFRA/` in Python 3.11:

```bash
python -m pip install -e .
export ML_DATABASE_URL='postgresql://postgres:...@127.0.0.1:5432/agentdb'
export ML_TIMESCALE_URL='postgresql://postgres:...@127.0.0.1:5433/stock'
python -m ml_infra.train --symbol IBM --require-gpu --output artifacts/candidate.json
export ML_ARTIFACT_PATH=artifacts/candidate.json
export ML_MODEL_TOKEN='replace-with-local-token'
uvicorn ml_infra.serve:app --host 127.0.0.1 --port 8000
```

In PowerShell use `$env:ML_DATABASE_URL=...`, `$env:ML_TIMESCALE_URL=...`, and `Copy-Item`. INFRA port forwards or a network route must be active. The model service reads Citus/Postgres and TimescaleDB for `/features/{symbol}` and responds to `/predict`; it does not write stock predictions.

### Manual deployment equivalent

After reviewing `candidate.json`, use the correct Kubernetes context and an image registry or kind image load path. These commands have not been run in this environment:

```bash
docker build -t stock-model:candidate .
kind load docker-image stock-model:candidate --name local-platform
kubectl --context kind-local-platform apply -f ../INFRA/kubernetes/namespaces/namespaces.yaml
kubectl --context kind-local-platform -n logistic-regression create secret generic stock-model-db-urls \
  --from-literal=postgres_url="$ML_DATABASE_URL_IN_CLUSTER" \
  --from-literal=timescale_url="$ML_TIMESCALE_URL_IN_CLUSTER" \
  --from-literal=model_token="$ML_MODEL_TOKEN"
helm upgrade --install stock-model ./helm/stock-model \
  --kube-context kind-local-platform --namespace logistic-regression \
  --values ./helm/stock-model/values.yaml --wait --timeout 5m
kubectl --context kind-local-platform -n logistic-regression rollout status deployment/stock-model
kubectl --context kind-local-platform -n logistic-regression port-forward svc/stock-model 8000:8000
```

In-cluster URLs use `citus-coordinator.postgres.svc.cluster.local:5432/agentdb` and `timescale.timescale.svc.cluster.local:5432/stock`; `127.0.0.1` will not reach these services from a pod. Use restricted DB roles for production. In `stock/`, set `STOCK_MODEL_URL`, `STOCK_MODEL_TOKEN`, and `STOCK_DATABASE_URL`, then run `python -m stock_research.predict --symbol IBM`. The resulting `stock_summary_daily` is model-only. An hourly summary requires licensed intraday bars and an hourly feature/target contract.

## Ownership

- `stock/` owns licensed ingestion, prediction orchestration, calls to hosted models, prediction persistence, summaries, human feedback, final LLM synthesis, and the stock-domain API. Its ingestion component only collects and stores facts.
- `ML_INFRA/` owns the first model's feature extraction from stock databases, training datasets and labels, model training/evaluation, immutable artifacts, model serving deployments, and rollback. It does not invoke models for the stock workflow or write stock predictions or summaries.
- `INFRA/` owns the kind/Kubernetes cluster, databases, namespaces, networking, persistent storage, and the infrastructure settings. ML_INFRA deploys its workloads **into** that cluster without creating a second cluster or database stack.
- The final LLM synthesis runs in `stock/` over a bounded point-in-time summary; deterministic risk policy remains in code. Execution stays paper-only or human-approved.

## First implementation target

1. Agree with `stock/` on the versioned feature and prediction API contracts.
2. Read historical stock outputs and matured outcomes to build a point-in-time training dataset.
3. Compare a five-trading-day logistic baseline with gradient-boosted trees on chronological holdouts.
4. Register an immutable artifact and require human approval before activation.
5. Deploy a private versioned model endpoint into the existing INFRA cluster; `stock/` calls it and saves predictions.
6. Consume later `stock_summary_hourly` results and human feedback for evaluated retraining and redeployment.

The model endpoint is private and only responds to stock workflow requests. `stock/` decides when to call it; neither training nor LLM synthesis runs on every price tick.

## Planned layout

```text
ML_INFRA/
  README.md
  PROJECT_PLAN.md
  pyproject.toml                 # package and optional training/serving dependencies
  src/ml_infra/
    contracts/                  # model input/output, feature-version, artifact schemas
    datasets/                   # point-in-time dataset builder and label definitions
    feature_adapter/            # consumes the versioned stock feature contract
    training/                   # baselines, tuning, calibration, and evaluation
    registry/                   # artifact manifest and approval/promotion
    serving/                    # private deployed model endpoint
    feedback/                   # outcome and human-feedback dataset ingestion
    monitoring/                 # model quality, drift, and serving health
  deployment/                   # model-serving Helm chart or manifests
  tests/                        # leakage, API, replay, and promotion tests
```

The subdirectories above describe later extensions; the first logistic model is implemented in the top-level `src/ml_infra/*.py` modules and `helm/stock-model/`. Keep secrets, trained artifacts, and large datasets out of Git.
