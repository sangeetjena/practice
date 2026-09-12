# ObserveAgent — agentic observability learning service

ObserveAgent starts when an incident is created. It extracts reproducible features from
Prometheus, retrieves approved operational knowledge, builds evidence-backed hypotheses, and
records reviewed incident resolutions as new versioned knowledge.

This is a runnable teaching implementation. The default reasoner is deterministic so tests and
debugging do not require an LLM account. A production implementation can replace the reasoner and
embedding provider without changing the incident, feature, retrieval, feedback, or policy boundaries.

## Important correction about signal storage

Prometheus stores **metrics**, not the lab's logs and traces. The existing API stack exports metrics
through the OpenTelemetry Collector to a Prometheus scrape endpoint. Traces go to Jaeger. Logs are
JSON on container stdout. ObserveAgent currently implements the Prometheus feature adapter and keeps
interfaces narrow so Jaeger and a future log-store adapter can be added separately.

## Components

| Component | File | Input | Output |
|---|---|---|---|
| Feature ETL | `observe_agent/features.py` | Incident + Prometheus queries | Current, baseline, delta, query and missing-source flags |
| Chunker/embedding | `observe_agent/knowledge.py` | Markdown runbooks and resolutions | Bounded chunks plus deterministic embeddings |
| Vector store | `observe_agent/knowledge.py` | Chunks, metadata and embeddings | SQLite hybrid vector/lexical search with tenant filters |
| Resolution collector | `observe_agent/agent.py` | Reviewed feedback and confirmed resolution | Versioned, approved incident-resolution chunks |
| Reflexion workflow | `observe_agent/agent.py` | Incident, features and retrieved knowledge | Ranked hypotheses, actions, unknowns and citations |
| Trigger API | `observe_agent/api.py` | Incident or Alertmanager webhook | Stored incident and triage report |
| Baseline reasoner | `observe_agent/reasoner.py` | Features and search hits | Explainable report without external model calls |

## Start locally

From `API` after installing the root project:

```powershell
$env:PYTHONPATH = "src;ObserveAgent"
$env:PROMETHEUS_URL = "http://localhost:9090"
python -m observe_agent.api
```

Bash uses `export PYTHONPATH=src:ObserveAgent`. Open http://localhost:8090/docs.

With the complete lab:

```powershell
python scripts/bootstrap.py
docker compose up --build -d
```

Prometheus rules route firing alerts through Alertmanager to
`http://observe-agent:8090/v1/alerts`. The HTTP endpoint performs triage synchronously for clarity.
A production service should first persist the webhook, enqueue its incident ID, return quickly, and
let idempotent workers perform investigation.

## Manual learning flow

Ingest or version a runbook:

```powershell
$env:PYTHONPATH = "src;ObserveAgent"
python -m observe_agent ingest ObserveAgent/data/runbooks/commerce-latency.md --service all
```

Create an incident using `POST /v1/incidents` or:

```powershell
curl.exe -X POST http://localhost:8090/v1/incidents `
  -H "Content-Type: application/json" `
  --data-binary "@ObserveAgent/data/sample-incident.json"
```

After a human verifies and resolves it:

```powershell
curl.exe -X POST http://localhost:8090/v1/incidents/inc-demo-001/feedback `
  -H "Content-Type: application/json" `
  --data-binary "@ObserveAgent/data/sample-feedback.json"
```

Only `accept` or `edit` feedback with `resolved=true`, a confirmed root cause, and a resolution is
indexed for retrieval. Rejected, incomplete, or unresolved feedback is retained for audit but is not
presented to later incidents as approved knowledge.

Read [the architecture walkthrough](docs/ARCHITECTURE.md), then follow
[the debugging guide](docs/DEBUGGING.md) to trace every stored input and output.
