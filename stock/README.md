# Stock research system

An auditable, event-driven Python foundation for stock analysis. The Alpha Vantage provider pulls daily OHLCV, company overview, and news; storage adapters persist events and decisions to Citus/Postgres, bars to TimescaleDB, embeddings to Qdrant, and ephemeral cache to Redis. Agents remain interfaces. No live broker execution is provided.

## Start locally

From `stock/`:

```bash
python -m venv .venv
./.venv/Scripts/python -m pip install -e ".[db,dev]"  # Windows PowerShell
# On macOS/Linux: .venv/bin/python -m pip install -e ".[db,dev]"
cp .env.example .env  # use Copy-Item on PowerShell
# Configure INFRA/.env and deploy from repository-root INFRA/ (see its README).
# Keep `make expose-all` running there when using local port-forwards.
./.venv/Scripts/python -m stock_research.ingest init-db
./.venv/Scripts/python -m stock_research.ingest daily --symbol IBM
./.venv/Scripts/python -m stock_research.ingest fundamentals --symbol IBM
./.venv/Scripts/python -m stock_research.ingest news --symbol IBM
# Premium entitlement only: enable STOCK_ALPHA_VANTAGE_INTRADAY_ENABLED in .env
./.venv/Scripts/python -m stock_research.ingest intraday --symbol IBM
./.venv/Scripts/python -m pytest
./.venv/Scripts/python -m uvicorn stock_research.api.app:app --reload
```

The health endpoint is `GET /health`. The repository's existing `INFRA/` owns development infrastructure, including the TimescaleDB and Redis services added with these adapters. Set its credentials in `INFRA/.env` and the matching connection URLs in `stock/.env`; neither file belongs in Git. `init-db` creates idempotent application tables and the Timescale hypertable. `daily` uses the provider's latest 100 bars and fails if the requested start predates its available compact window. Fundamental `OVERVIEW` is a current snapshot, not a historical point-in-time reconstruction. Alpha Vantage intraday data requires a premium entitlement and is disabled by default. Provider access may also be limited by plan, exchange rights, and API quota. No API key or running database was available for a live integration test in this session. `STOCK_EXECUTION_MODE` is restricted to `paper` or `human_approved`.

Data ownership: Citus/Postgres stores source events, stock contexts, decisions, and critiques; TimescaleDB stores OHLCV bars; Qdrant stores embeddings supplied by a future embedding pipeline; Redis stores short-lived cache entries and cooldowns. Cassandra remains part of `INFRA/` but has no stock adapter because this phase has no Cassandra workload. The ingestion command writes source events to Postgres and bars to TimescaleDB. It does not invent embeddings or call an LLM.

## Layout

- `ai_skill/SKILL.md`: durable project brief, architecture, invariants, schema, and delivery plan.
- `src/stock_research/domain`: validated contracts and decision lifecycle.
- `providers`, `storage`: source and persistence ports plus Alpha Vantage, Postgres, TimescaleDB, Qdrant, and Redis implementations.
- `rules`: deterministic versioned trigger evaluation.
- `themes`: extensible candidate discovery contract.
- `agents`, `workflows`: interpretation ports and orchestration boundaries.
- `telemetry`: AI invocation usage, cost, and trace contracts.
- `api`: read-oriented API scaffold.

## Development gates

```bash
python -m pytest
python -m ruff check src tests
python -m mypy src
```

Set API keys only in an untracked `.env`; use licensed data feeds and respect source terms. Start with historical replay and paper trading, then compare outcomes and costs before any human-approved order integration.
