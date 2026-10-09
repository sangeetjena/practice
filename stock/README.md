# Stock prediction â€” CrewAI + CSV memory

A compact CrewAI Flow project, initialized with the official classic generator:
`crewai create flow stock-research --classic --skip-provider`.
Agents/tasks are YAML-backed. CSV stores source snapshots, predictions and feedback.
The application makes no Postgres, Timescale or vector-store writes in this version.

## Structure

```text
stock/
  src/stock_research/
    main.py                  # CrewAI kickoff/plot and CLI
    config.py                # .env settings
    agents/
      data_ingestion/        # discovery, technical, fundamental, earnings, news
      analytical/            # volume, candlestick, Bollinger specialists
      master/                # final prediction and concise reasoning
      learner/               # lessons from historical outcomes/criticism
      critique/              # previous predictions against next-session outcomes
      # Each group: crew.py + config/agents.yaml + config/tasks.yaml
    models/                  # all documented Pydantic input/output contracts
    flow/                    # group Flows, master Flow, crew execution boundary
    tools/
      api/                   # Alpha Vantage, screener, local ML HTTP client
      db/                    # retained connectors and SQL; unused by this workflow
      market.py              # online data extraction and deterministic indicators
      indicators.py          # reused indicator calculations
      csv_memory.py          # atomic CSV memory and monthly fundamental cache
      review.py              # deterministic outcomes and historical selection
      agent_tool.py          # CrewAI BaseTool adapter
      offline.py             # explicit synthetic test fixtures
  examples/watchlist.csv
  knowledge/research.md       # editable reference knowledge for master agent
  tests/
  docs/RUNBOOK.md
  ai_skill/SKILL.md
```

## Setup and test

Use Python 3.12 from `stock/`. Preserve the existing untracked `.env`.

```bash
uv venv --python 3.12 .venv-crewai-wsl  # first WSL/Linux setup only
source .venv-crewai-wsl/bin/activate
uv pip install -e '.[dev]'
python -m stock_research.main --offline --stocks IBM --output output.md
python -m pytest -q
```

For PowerShell use a separate Windows environment:

```powershell
uv venv --python 3.12 .venv-crewai  # first Windows setup only
./.venv-crewai/Scripts/Activate.ps1
uv pip install -e ".[dev]"
python -m stock_research.main --offline --stocks IBM
```

Reuse the appropriate existing environment; do not share a virtual environment between Windows and WSL.

Offline uses synthetic data/agent stand-ins and isolates CSV under `data/offline/`.
It runs the real Flow/tool contracts without API credentials or model calls.
Live mode runs actual CrewAI agents and requires LLM credentials:

```bash
python -m stock_research.main --stocks IBM MSFT
# Or configure watchlist/.env and use the generated CrewAI entrypoint:
crewai run
```

Outputs: `data/ingestion.csv`, `data/fundamentals.csv`, `data/stock_memory.csv`,
and verbose workflow steps in `output.md`. See [the runbook](docs/RUNBOOK.md)
for configuration, exact CSV columns, execution order, cache expiry and review semantics.

The older API, database-writing ingestion CLI and mixed research scaffolding were
removed. Future database/vector-store integration belongs behind `tools`.
The retained ML HTTP client is available for future integration; this version's
three specialist agents interpret source indicators directly. No trade execution.
