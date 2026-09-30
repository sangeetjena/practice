---
name: stock-research-project
description: Continue and evolve the stock research system in this repository, preserving point-in-time evidence, deterministic triggers, auditable AI decisions, and paper or human-approved execution.
---

# Stock research project knowledge

Read this before changing `stock/`. The user wants an extensible AI-assisted stock analysis and trading-research system, initially for research, monitoring, and paper trading. The product must explain what was known, what was predicted, what happened later, which model was used, and what each invocation cost. Do not add real-money autonomous execution.

## Core design

Deterministic programs ingest and normalize feeds, calculate indicators, evaluate versioned rules, monitor holdings, and schedule work. LLM agents run only for meaningful events or scheduled analysis to interpret, correlate, decide, or critique. Never call an LLM on each price tick. A condition such as `price crosses resistance AND volume_ratio > 2 AND RSI crosses 60` is approved, versioned code or declarative configuration executed by the rule engine. An LLM may propose a rule change but cannot silently activate it or rewrite its own knowledge base.

## Operating workflows

**Live monitoring:** Stream or poll licensed market data for held and watched stocks during market hours. Normalize exchange timestamps and data availability timestamps; maintain rolling bars and indicators. Rule triggers such as stop or target approach, support or resistance break, volume anomaly, trend reversal, or material news enqueue a debounced, idempotent analysis. Apply cooldowns, data-quality gates, and per-symbol rate limits. The risk agent can suppress a recommendation. An approved paper order or a human approval request is the only execution path.

**Batch research:** Each trading day, refresh price and technical features, news, sentiment, sector and macro context, and discovery themes for the watchlist and candidates. Recompute fundamentals for covered stocks about monthly and also on earnings or material filings; store every version with source and effective time. Run themes such as hot sectors, upcoming earnings, political or global events, and future plugins. Deduplicate candidates before agent analysis. Backfill and historical replay use the same contracts with a simulated clock.

**Critique:** At the prediction horizon or a defined invalidation event, load the immutable decision snapshot, original evidence available by its cutoff, actual subsequent price path, and later events. Compute objective outcome metrics first (target/stop touch order, drawdown, return, benchmark-relative return, horizon). Ask the critique agent to distinguish an error in the original inference, omitted information that was already available, data quality, and genuinely new information after the decision. It must cite evidence IDs and observation times and may report inconclusive. It does not retroactively add later news to the original context. Store critiques separately, linking the original decision; do not overwrite the original rationale.

## Per-stock durable context and thesis

Postgres is the source of truth. `stock_context` is a materialized per-symbol view, not chat history: active thesis and status, open paper position, latest decision and rationale, active risks, watch conditions, approved lessons, relevant event IDs, and context version. A context builder assembles a bounded, point-in-time snapshot before each invocation. Use source priority, freshness, token budget, and explicit cutoff; retrieve relevant older decisions and critiques from indexed records or pgvector only if they were available by the cutoff. Record the exact snapshot hash and all evidence refs with each decision. Optimistic versioning prevents stale writes.

Thesis lifecycle: `proposed → active → challenged → invalidated → closed` (a challenged thesis may return to active after evidence). New decisions compare the prior thesis, watch conditions, new evidence, and position state. Preserve thesis history and state transitions rather than editing old predictions. Lessons are candidate notes until reviewed and approved.

## Component ownership

- **Providers/ingestion:** Market bars and volume, corporate actions, fundamentals, earnings calendar, news, sector composition, macro series. Adapters expose source, event time, observed/available time, revision, licensing, and stable source IDs; deduplicate and quarantine bad data. Avoid unauthorized website scraping.
- **Indicators and rules:** Pure Python or vectorized calculations for RSI, EMA/SMA, ATR, volume ratio, relative strength, trend, support/resistance, breakout and crossovers. Specify bar interval, adjustment policy, lookback, missing-data behavior, market calendar, thresholds, cooldown, and rule version. Unit-test with known series and replay.
- **Themes:** Registry of versioned plugins with `discover(as_of) → candidates` and evidence. Hot sector, earnings, and macro/political themes should emit candidates, not orders. Apply common quality and risk filters.
- **Technical agent:** Interpret patterns and indicator context only from computed features and chart evidence.
- **Fundamental agent:** Interpret filings, valuation, financial health and revision deltas; avoid fabricating metrics.
- **News agent:** Summarize and classify source-grounded news, novelty, affected symbols, and publication/availability time.
- **Sector agent:** Compare peers, breadth, flows, and relative strength.
- **Macro agent:** Relate rates, FX, policy and global events to symbols/sectors with uncertainty.
- **Risk agent:** Enforce position limits, concentration, liquidity, data freshness, conflicting signals, and stop/target logic in deterministic policy; explain vetoes.
- **Decision agent:** Combine findings into `ENTER`, `HOLD`, `REDUCE`, `EXIT`, or `WATCH` with horizon, confidence, target/stop when meaningful, rationale, citations, uncertainty and invalidation conditions. Persist immutable snapshot before exposing a recommendation.
- **Critique agent:** Perform the retrospective separation described above; propose improvements only.

## Rule improvement governance

Capture an improvement proposal with originating critiques, hypothesis, exact rule or prompt diff, scope, owner, and expected failure mode. Run leakage-safe, point-in-time backtests with train/validation/test periods, walk-forward or out-of-sample evaluation, transaction costs, slippage, corporate actions, market regimes, and comparison with the current rule. Report false positives, precision, drawdown, risk-adjusted return, turnover, sample size, and uncertainty. A reviewer approves or rejects a versioned proposal; approval is required before promotion. Stage in shadow mode and paper trading, monitor drift, and keep rollback path. Prompt changes follow the same evaluation and approval trail. No automatic self-modification from critique text.

## Data and schema plan

Use Postgres for relational truth and transactions; TimescaleDB hypertables for bars, quotes, indicators, event measurements, and telemetry by time; pgvector for optional similarity search over source-grounded document/lesson embeddings; Redis for queues, cooldowns, ephemeral cache, locks and rate limits. Redis is never the sole record of a decision. Excel/CSV can be export or review surfaces, not the canonical event store.

Repository-root `INFRA/` owns provisioning. It deploys PostgreSQL/Citus, Cassandra, Qdrant, TimescaleDB, and Redis. Do not create infrastructure under `stock/`. Use the separate TimescaleDB PostgreSQL instance for bars and Citus/Postgres for durable events, contexts, decisions and critiques. Qdrant is the vector store; pgvector remains an optional future alternative. Redis is an ephemeral cache/cooldown service. The Alpha Vantage adapter pulls daily OHLCV, company overview, and news; intraday polling is gated by premium entitlement. See `stock/README.md` for initialization and ingest commands. Keep historical replay point-in-time safe: a current company overview cannot be backdated to an earlier decision.

Initial tables and key fields:

- `instruments(symbol, exchange, currency, calendar, sector, active)`; `positions(id, symbol, mode, quantity, entry_time, entry_price, status)` and `paper_orders(id, position_id, approval_id, state, created_at)`.
- `market_bars(symbol, interval, bar_time, observed_at, open, high, low, close, volume, adjusted, provider, revision)` hypertable keyed by symbol/interval/time; `indicator_values(symbol, interval, time, name, value, params_hash, input_revision)` hypertable.
- `source_events(id, symbol, type, occurred_at, observed_at, source, source_id, payload, revision)` with source-ID uniqueness and separate source documents/embeddings. Never infer availability from publication alone.
- `themes(id, version, config, active)` and `theme_candidates(id, theme_id, version, symbol, as_of, evidence_ids)`.
- `rules(id, version, definition, state, approved_by, approved_at)` and `rule_triggers(id, rule_id, version, symbol, event_time, metrics, dedupe_key)`.
- `theses(id, symbol, status, narrative, created_at, updated_at, version)` plus append-only `thesis_transitions`; `stock_context(symbol, version, as_of, state)` with optimistic concurrency.
- `decisions(id, symbol, decided_at, cutoff_at, action, horizon, confidence, target, stop, rationale, rule_version, prompt_version, agent_version, context_version, snapshot_hash, evidence_ids)` and immutable `decision_snapshots(id, full_input, model_output, content_hash)` with sensitive text controls.
- `critiques(id, decision_id, evaluated_at, outcome, original_reasoning_issue, later_invalidation, metrics, original_evidence_ids, subsequent_event_ids)`; `improvement_proposals(id, status, change, backtest_id, reviewer, approved_at)`; `backtest_runs(id, data_cutoff, code_version, parameters, metrics, artifacts)`.
- `workflow_runs(id, kind, symbol, idempotency_key, state, scheduled_at, started_at, finished_at, trace_id)` and `ai_invocations(event_id, trace_id, span_id, workflow_run_id, decision_id, symbol, agent_name, agent_version, prompt_version, provider, model, model_version, started_at, ended_at, latency_ms, input_tokens, output_tokens, cached_input_tokens, reasoning_tokens, total_cost_usd, tool_calls, status, error_type)`; include `pricing_version` and raw provider usage JSON in implementation.

Use UTC timestamps in storage, preserve exchange timezone and calendar metadata, and make `(source, source_id, revision)` and workflow idempotency keys unique. Partition and retain high-volume series intentionally; keep decisions and audit records longer. Encrypt or tightly control sensitive source content and credentials. Migrations must be reversible where feasible and tested on a disposable database.

## Orchestration and model routing

Begin with an async API plus a scheduler and worker queue. Use APScheduler for local schedules and Redis-backed jobs or a durable queue with idempotent worker claims for deployments; move to Temporal or equivalent only if recovery complexity warrants it. State transitions: `queued → running → succeeded/failed`, with `waiting_for_approval` for gated actions; retries use backoff, bounded attempts, and stable idempotency keys. Market calendar determines hours and holidays. Separate live monitoring, daily research, monthly fundamentals, critique, and backtest queues to control latency and spend.

Use a low-cost model for extraction/classification and concise news summaries, a stronger reasoning model for decision synthesis or difficult critique, and deterministic code for indicators, outcome scoring and risk limits. Route by task difficulty and confidence; use provider-neutral adapters. Record exact model/version, prompt/agent versions, usage and cost per invocation. Budget by symbol/workflow/day and skip redundant calls. Do not hard-code a model brand or assume provider usage fields are always present.

Suggested stack: Python 3.11+, Pydantic and pydantic-settings, FastAPI, SQLAlchemy/asyncpg and Alembic, TimescaleDB/Postgres, pgvector, Redis, pandas or Polars and NumPy for research, TA-Lib or `pandas-ta` only after license/build review, APScheduler for the first scheduler, OpenTelemetry for traces, Prometheus/Grafana for metrics, pytest/Ruff/mypy, Docker Compose for development. Evaluate feed and broker SDKs against market coverage, latency, licensing, and paper-trading support before selecting them.

## API and observability

Plan read endpoints for instruments, per-stock context, decisions with evidence, critique, rule versions, theme candidates, workflow status, telemetry/cost summaries, and backtest reports. Write endpoints for watchlists, research requests, improvement proposals, and explicit approvals require authenticated roles, audit entries, and idempotency keys. An approval does not bypass risk checks.

Every ingest event and workflow carries event/trace/span IDs. Record timestamps, latency, queue time, tool calls, token usage (input/output/cached/reasoning when provider exposes it), total cost, pricing version, errors, rule/agent/prompt/model versions, and decision link. Keep structured logs with IDs, metrics for freshness, queue lag, trigger volume, model spend, token usage, decision outcome and data quality, and traces across ingestion → rule → context → agents → decision → critique. Avoid storing raw secrets or unnecessary personal data in logs or prompts. Alert on stale feeds, failed jobs, unbounded spend, missing usage, and risk-gate violations.

## Testing and security gates

Test indicator mathematics, crossing semantics, missing data, timezones/market calendars, idempotency and cooldowns, context optimistic locking, rule approvals, and critical risk vetoes. Replay recorded fixtures through the same event pipeline. Test critique with a post-decision event that must not be labeled an original mistake. Backtests enforce point-in-time joins and no lookahead or survivorship leakage. Contract-test adapters and verify telemetry against provider responses. CI should run unit tests, lint, types, dependency/security checks, and migration smoke tests.

Keep credentials in secret storage or local untracked `.env`; least-privilege feed, database, model, and paper-broker accounts; TLS; role-based API access; audit all approvals. Validate and sanitize external text because news and pages are untrusted prompt input. Enforce rate limits and cost limits. Never place order credentials in the first implementation or enable real-money autonomous execution.

## Phased execution plan

1. **Foundation (this PR):** Package, contracts, rule/theme/agent/storage/telemetry ports, local infrastructure, runbook, basic tests, and this project brief. This is scaffolding, not a functioning trading system.
2. **Data and deterministic core:** Pick licensed providers and market, create migrations and adapters, ingest bars/news/fundamentals, normalize timestamps/corporate actions, implement indicators and replayable rule engine.
3. **Context and research:** Durable thesis transitions and context builder, theme registry, scheduled daily/monthly analysis, technical/fundamental/news/sector/macro/risk/decision agents, immutable decision snapshots, API reads.
4. **Monitoring and paper trading:** Market-hours worker, event gating, alerts, risk checks, paper positions and explicit approval UI/API, operator runbooks.
5. **Critique and improvement:** Outcome scoring, critique job, evidence-cited attribution, proposal workflow, leakage-safe backtesting, approval and shadow deployment.
6. **Production readiness:** SLOs, cost budgets, tracing dashboards, retention/backups, access control, resilience tests, security review, and extended paper-trading evaluation.

For each phase, document selected data/model providers, assumptions, schema changes, replay results, cost and failure modes. Do not present untested research signals as investment advice.
