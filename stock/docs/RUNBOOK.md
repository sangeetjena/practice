# Runbook

## 1. Configure

From `stock/`, use a separate Python 3.12 virtual environment and install `.[dev]`.
WSL/Linux: `.venv-crewai-wsl/bin/activate`; PowerShell: `.venv-crewai/Scripts/Activate.ps1`.
Reuse the matching environment; Windows and WSL cannot share one virtual environment.
Copy `.env.example` only if `.env` does not already exist. Preserve existing keys.
For live agents set `OPENAI_API_KEY` (or the configured provider's credentials),
`STOCK_RESEARCH_LLM`, and optionally `STOCK_RESEARCH_LLM_BASE_URL`.
Set `STOCK_ALPHA_VANTAGE_API_KEY` to reuse the existing US price/fundamental caller.
Without it, Yahoo is used. India exchange symbols use `.NS` or `.BO`.
News and earnings currently use Yahoo. Quotas, unavailable metrics and coverage
depend on the source; no live provider or LLM integration is implied by offline tests.

Watchlist file: a CSV with a `stock` header and uppercase exchange tickers.
Set `STOCK_WATCHLIST_FILE=examples/watchlist.csv`, or supply `--stocks IBM MSFT`.
If no watchlist exists, discovery uses the bounded screener. India discovery
requires `STOCK_SCREENER_INDIA_CSV`, the normalized export contract retained in
`tools/api/screener.py`. Screener.in has no public API. Explicit watchlists need
no screener. `--stocks` with no tickers explicitly requests discovery.


### Agent model configuration

All agents currently use `gemini/gemini-3.1-flash-lite`. Set `GEMINI_API_KEY`
in your untracked `.env` and install the project's `crewai[google-genai]` dependency.
Every `agents.yaml` uses `llm: agent_llm`, which resolves through the shared
CrewAI LLM factory, including its temperature and timeout settings.
Change `STOCK_RESEARCH_LLM` in `.env` to switch every agent together.
For a per-agent override later, replace that agent's YAML `llm` with a full
provider/model string. Restart the application after changing configuration.
An exported shell variable takes precedence over `.env`; update or unset it
if the previous model continues to be used. Free API quotas still apply.

## 2. Execute

```bash
python -m stock_research.main --stocks IBM --market US
python -m stock_research.main --offline --stocks IBM --output output.md
python -m stock_research.main --offline --stocks IBM --as-of 2026-10-06T20:00:00Z
python -m stock_research.main --offline --stocks IBM --as-of 2026-10-07T20:00:00Z
python -m pytest -q
python -m ruff check src tests
```

The two dated offline runs demonstrate durable memory and next-session review.
Offline output is explicitly synthetic and recommendations abstain. Its CSV
directory is always `<STOCK_DATA_DIR>/offline`, separated from live history.
Live mode refuses historical cutoffs: current fundamental/news APIs are not a
point-in-time replay dataset. --as-of is for synthetic replay testing only.
Use --quiet or STOCK_RESEARCH_VERBOSE=false to reduce console output.

`crewai run` invokes the generated `kickoff` script defined in pyproject.toml.
`crewai install` uses uv to install the project; `crewai run` can use its `.venv`.
For an explicitly chosen `.venv-crewai`, use the module command after activation.
`plot` generates `stock_flow.html` from the master Flow's decorators.

## 3. Execution sequence

```text
CLI/CrewAI entrypoint â†’ StockResearchFlow
  discovery crew â†’ selected watchlist
  DataIngestionFlow
    technical + fundamental + earnings + news tasks (asynchronous)
    synchronization task â†’ immutable typed snapshot â†’ ingestion.csv
  CritiqueFlow â†’ next-session objective outcome â†’ update older CSV row
  LearnerFlow â†’ historical accuracy and suggestions
  AnalyticalFlow
    volume + candlestick + Bollinger tasks (asynchronous)
    synchronization task â†’ three typed predictions
  MasterPredictionFlow â†’ facts + predictions + knowledge + lessons
  append stock_memory.csv â†’ output.md
```

Stocks run sequentially to bound provider/LLM pressure. Independent tasks inside
each group use CrewAI `async_execution: true`, followed by one synchronous task
with explicit `context` dependencies to wait for all branches. `akickoff()` starts
each crew. `@start` / `@listen` connect group Flows in the master Flow.
Classic `@CrewBase`, `@agent`, `@task`, `@crew`, `@tool`, `@llm` map YAML names
to Python factories. YAML contains every agent/task definition. Python binds
the source tool and validates results. Actual source numbers cannot be replaced
by the agent's generated values; ingestion mismatches fail the run.

## 4. CSV memory

`stock_memory.csv` has one row per stock prediction. Columns:

```text
prediction_id, date, stock, current_price,
technical_indicators, fundamental_indicators, fundamental_fetched_at, news, earnings,
rsi14, volume, volume_ratio20, bollinger_upper, bollinger_middle, bollinger_lower,
pe, market_cap, eps, debt_to_equity,
volume_prediction, volume_reasoning,
candlestick_prediction, candlestick_reasoning,
bollinger_prediction, bollinger_reasoning,
master_prediction, master_reasoning, master_confidence, learner_lessons,
critique_verdict, critique_suggestion, critique_date, actual_return, record
```

`record` contains the complete validated ResearchRow as JSON, including exact
source bars/articles, analytical outputs, original master result and critique.
Nested dictionaries/lists use JSON inside properly quoted CSV cells. `date` is
the UTC-aware observation timestamp, so multiple runs retain time-series history.
`current_price` is the last completed daily close, not a live intraday quote.
There is one master_prediction column; the duplicated name in the requested
example is represented once. Files are ignored by Git.

`ingestion.csv` stores each stock's source snapshot before analysis. Fundamentals
are append-only in `fundamentals.csv`; the newest eligible observation is reused
until one calendar month expires. January 31 expires February 28/29, not a fixed
30-day approximation. Historical/future entries cannot satisfy the current cache.
The reusable fundamental tool owns expiry; the LLM cannot override it. CrewAI
vector memory is disabled: CSV is the memory for this iteration. Bound tools
load relevant CSV history for learner and critique. Reference knowledge is the
local Markdown file configured by STOCK_KNOWLEDGE_FILE, supplied to master;
no embedding/vector database is required.

## 5. Review and learning

Master direction is UP, DOWN, FLAT or INSUFFICIENT_EVIDENCE for the next completed
trading session. Code compares the original close with the FIRST later completed
bar. A +/-0.1% deadband defines FLAT. Verdict is CORRECT, INCORRECT or INCONCLUSIVE;
abstentions are inconclusive and excluded from accuracy. No review happens when
there is no later completed bar (weekends/holidays included). If the original bar
is outside available history, review waits rather than selecting an arbitrary
later price. Daily bars are conservatively usable after timestamp +24 hours.

Critique receives later bars/news limited to the scored interval, so events after
the outcome cannot be used to explain it. Critique adds feedback to the original row without changing its evidence or
prediction. It receives separate original/later packets. Learner reads up to 30
evaluated historical outcomes at/before the current cutoff, computes accuracy in
code, and proposes lessons. Master receives those lessons on the same run after
review. This is prompt/context improvement, not model retraining or proof of
accuracy. Interpretations are LLM-generated; independent evaluation is needed.

## 6. Operations and future extensions

CSV writes use file locks and atomic replacement. A process lock prevents two
master runs using the same memory directory. Schedule the module command with
your OS scheduler after daily source bars are complete; no always-running LLM.
Keep one shared memory directory and one output path per scheduler. Exceptions
write an error type to output.md; provider credentials/DSNs are never logged.
If a run fails, source ingestion/fundamentals may already be present. Inspect
output.md before retrying; final predictions are saved only after master finishes.
No retry recovery queue, database writes, or automatic broker execution exists.

Existing Postgres/Timescale/Qdrant/Redis connectors and SQL are retained in tools/db
and never imported by active Flows. Install .[db] when using those connectors in
the next iteration. Local ML HTTP caller is tools/api/local_model.py. Source and
future storage implementations should preserve the documented Pydantic contracts.

Official references used: [classic YAML crews](https://docs.crewai.com/v1.15.23/en/concepts/crews),
[Flows](https://docs.crewai.com/v1.15.23/en/concepts/flows),
[project quickstart](https://docs.crewai.com/v1.15.23/en/quickstart).

### Missing tool calls or changed source values

Every evidence-backed task has a programmatic CrewAI guardrail. If an agent
answers without successfully calling its bound tool, returns invalid JSON, or
changes ingestion facts, CrewAI sends correction feedback to that task and
allows at most two retries (`guardrail_max_retries` in tasks.yaml).
News may rewrite its summary but must preserve articles and metadata.
A source failure or repeatedly skipped tool still fails the run; it never becomes
a fabricated recommendation. Successful source calls remain cached across retries.
Retries consume additional model quota. This is task-local recovery, not rerunning
the whole stock workflow. Inspect verbose task output for tool errors if retries
are exhausted.
