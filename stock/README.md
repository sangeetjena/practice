# Stock research system

An auditable, event-driven Python foundation for stock analysis. Deterministic code ingests data, calculates indicators, and evaluates versioned rules. Agents are invoked for interpretation, correlation, decisions, and retrospective critique. No live broker execution is provided.

## Start locally

From `stock/`:

```bash
python -m venv .venv
./.venv/Scripts/python -m pip install -e ".[dev]"  # Windows PowerShell
# On macOS/Linux: .venv/bin/python -m pip install -e ".[dev]"
cp .env.example .env  # use Copy-Item on PowerShell
docker compose -f infra/compose.yaml up -d
./.venv/Scripts/python -m pytest
./.venv/Scripts/python -m uvicorn stock_research.api.app:app --reload
```

The health endpoint is `GET /health`. Database containers are development dependencies; persistence adapters, migrations, feeds, model calls, and workers are next-phase work, so this scaffold makes no live market recommendation. `STOCK_EXECUTION_MODE` is restricted to `paper` or `human_approved`.

## Layout

- `ai_skill/SKILL.md`: durable project brief, architecture, invariants, schema, and delivery plan.
- `src/stock_research/domain`: validated contracts and decision lifecycle.
- `providers`, `storage`: source and persistence ports.
- `rules`: deterministic versioned trigger evaluation.
- `themes`: extensible candidate discovery contract.
- `agents`, `workflows`: interpretation ports and orchestration boundaries.
- `telemetry`: AI invocation usage, cost, and trace contracts.
- `api`: read-oriented API scaffold.
- `infra`: local development services.

## Development gates

```bash
python -m pytest
python -m ruff check src tests
python -m mypy src
```

Set API keys only in an untracked `.env`; use licensed data feeds and respect source terms. Start with historical replay and paper trading, then compare outcomes and costs before any human-approved order integration.
