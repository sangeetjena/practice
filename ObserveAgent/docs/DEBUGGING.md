Use [CONFIGURATION.md](CONFIGURATION.md) for ChromaDB, model and LangGraph settings.
Run Compose commands from `practice/API`; Python agent commands from `practice/ObserveAgent`.

# ObserveAgent debugging guide

Use this sequence so each failure is isolated before moving to the next layer.

## 1. Confirm source telemetry

Open Prometheus at http://localhost:9090 and run:

```promql
sum by(service) (rate(api_requests_total[5m]))
```

If there is no data, generate API traffic, then check the `otel` target under Prometheus targets.
Inspect `docker compose logs otel orders customers products`. Remember that Jaeger holds traces and
container stdout holds logs; their absence cannot be debugged with a Prometheus query.

## 2. Confirm the incident trigger

Inspect Prometheus Alerts. Rules require their `for` duration, so one slow request is insufficient.
Then inspect:

```powershell
docker compose logs --tail=100 alertmanager observe-agent
```

For isolation, bypass alerting and POST `data/sample-incident.json` directly. If manual
creation works, the failure is before ObserveAgent. If it fails, check request validation and service
identifier format in the JSON response.

## 3. Reproduce feature extraction

Every stored `MetricFeature` is derived from an exact query stored by the extractor.
Copy the query into Prometheus and evaluate it at the incident timestamp and baseline timestamp.

Common failures:

| Symptom | Likely boundary | Check |
|---|---|---|
| All values missing | Prometheus network/URL | `PROMETHEUS_URL`, container DNS, `/api/v1/query` |
| Only p95 missing | Histogram series absent | metric name, `le` label and recent requests |
| Error ratio is zero | No sustained 5xx traffic | rule window, status attribute and traffic volume |
| Values differ later | Time mismatch | use the incident timestamp, not only current time |

## 4. Inspect the knowledge database

The default Compose database is `/data/observe-agent.db` inside the container volume. Locally it is
`./observe-agent.db` unless `OBSERVE_DB_PATH` is set.

```powershell
docker compose exec observe-agent python -c "import sqlite3; c=sqlite3.connect('/data/observe-agent.db'); print(c.execute('select source_id,version,active from knowledge_chunks').fetchall())"
```

No runbook rows means startup bootstrapping failed or the bundled file is missing. A stored row that
is never returned usually has incompatible `tenant_scope`, `service`, or `review_status` metadata.

## 5. Debug retrieval

Use the same incident tenant and service when calling `ChromaKnowledgeStore.search`. Inspect chunk
scores, source IDs, metadata and the embedding profile. Hash collisions are possible in offline mode;
select a semantic embedding model for meaningful language similarity. Reindex after changing models.

Never fix a retrieval miss by removing tenant filters. Correct the source metadata or access policy.

## 6. Debug the report

Read the report in this order:

1. `known_facts`: directly measured values.
2. `hypotheses`: possible causes and confidence, not proven root causes.
3. `verification_queries`: evidence needed to falsify a hypothesis.
4. `recommended_actions`: review guidance before state changes.
5. `unknowns`: missing telemetry or knowledge that limits confidence.
6. `citations`: exact source and chunk IDs.

The default reasoner only understands the configured thresholds. If a report is generic, first
check whether features were present and thresholds were breached before changing reasoning logic.

## 7. Debug feedback and knowledge update

Feedback is always audited, but `knowledge_updated` is false unless decision is accept/edit,
`resolved=true`, and both root cause and resolution are present. This is intentional.

After accepted feedback, query `knowledge_chunks` for `incident-resolution:<incident-id>`. Create a
second similar incident for the same tenant and service; its report should cite the new source.
Another tenant must not retrieve it.

## 8. Full failure-injection exercise

1. Set `CUSTOMERS_DELAY_MS=1000` and restart customers.
2. Repeatedly call the orders customer-detail endpoint to fill the five-minute metric window.
3. Observe the slow orders → customers span in Jaeger.
4. Wait for the alert `for` duration or submit a manual incident.
5. Confirm the report includes latency facts and retrieves the commerce latency runbook.
6. Restore `CUSTOMERS_DELAY_MS=0`.
7. Submit reviewed feedback with the confirmed cause and resolution.
8. Create a similar incident and confirm the prior resolution is retrieved.

This exercise proves collection, detection, ETL, retrieval, reasoning, feedback, and versioned
knowledge separately. It does not prove autonomous remediation or production-scale model quality.
