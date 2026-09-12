# API Interview Lab

A small, runnable Python project for revising API design, client-side data extraction,
validation, concurrency, service deployment, and observability before an interview. Every
example uses the same sales-order API so you can compare approaches instead of learning
unrelated toy programs.

## Architecture and naming

```text
API/
├── src/api_interview_lab/
│   ├── client/       # HTTP transport, default headers, auth, sync/async pagination
│   ├── domain/       # Pure business concepts; no HTTP, database, or framework code
│   ├── patterns/     # Different ways to represent API responses
│   ├── data/         # Repository contract and SQLite implementation
│   └── server/       # FastAPI REST/GraphQL, security, health, and metrics
├── examples/         # Runnable API-client demonstrations
├── feeds/            # Seed data for the local simulation server only
├── tests/            # Unit and transport-level integration tests
├── deploy/           # Kubernetes and Prometheus Operator examples
└── ai_skills/        # Project knowledge for an AI coding assistant
```

`domain` means the core business vocabulary and rules. Here, `Order`, `OrderStatus`, and the
`revenue` calculation belong to the domain. They should remain usable if FastAPI is replaced
with Flask, SQLite with PostgreSQL, or REST with Kafka. Pydantic classes are transport models:
they validate untrusted JSON at the API boundary. Keeping these separate prevents framework and
wire-format details from leaking into business logic.

## Quick start

```bash
cd API
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -e '.[dev]'
python scripts/load_feed.py
uvicorn api_interview_lab.server.main:app --reload
```

Open REST/OpenAPI at <http://localhost:8000/docs>, GraphQL at
<http://localhost:8000/graphql>, and health probes at `/health/live` and `/health/ready`.
Then, in another terminal:

```bash
python examples/run_patterns.py
pytest
ruff check .
```

The CSV/JSON files only seed the local server. All examples in `patterns/` extract data from
`GET /api/v1/orders` through `SyncOrderClient`.

## Client, headers, and authentication

The client always supplies `Accept`, `Content-Type`, and `User-Agent`. Caller headers override
defaults, and authentication headers have final precedence.

```python
from api_interview_lab.client import BearerTokenAuth, SyncOrderClient

with SyncOrderClient(
    "http://localhost:8000",
    auth=BearerTokenAuth("interview-demo-token"),
    headers={"X-Correlation-Source": "interview-practice"},
    timeout=5.0,
) as client:
    raw_json = client.fetch_all_raw(page_size=50)
    validated_page = client.list_orders(page=1, page_size=10)
```

Available examples are `BearerTokenAuth`, `ApiKeyAuth`, and `BasicAuth`. The sample server
enforces Bearer authentication only when `API_TOKEN` is configured. In production, prefer an
identity provider using OAuth 2.0/OIDC, short-lived signed tokens, authorization scopes, TLS,
and a secret manager; never commit tokens.

## API extraction patterns

| Pattern | Function | What it returns | Use it when |
|---|---|---|---|
| Raw JSON + `TypedDict` | `extract_with_typed_dict` | `list[OrderDict]` | Static hints without runtime validation |
| Dataclass | `extract_with_dataclasses` | `list[OrderRecord]` | Trusted input and lightweight objects |
| Pydantic | `extract_with_pydantic` | `list[OrderPayload]` | Remote JSON needs runtime validation |
| pandas | `extract_with_pandas` | `DataFrame` | Bounded responses need local analytics |
| asyncio | `AsyncOrderClient` | objects or streamed pages | Independent network calls should overlap |

Other useful choices to mention in interviews include `msgspec` for fast typed JSON,
`attrs` for declarative classes, `polars` for multi-threaded local analytics, and `pyarrow` for
columnar memory/Parquet. Spark, Flink, or Beam fit distributed/streaming workloads. These are
alternatives, not dependencies here—the project stays intentionally small. Network retrieval
still belongs in the client; the modeling library should not make HTTP calls itself.

## REST and GraphQL

```bash
curl -H 'Authorization: Bearer interview-demo-token' \
  'http://localhost:8000/api/v1/orders?page=1&page_size=5'
curl http://localhost:8000/health/ready
curl http://localhost:8000/metrics
```

```graphql
query {
  orders(limit: 3) { id product revenue status }
}
```

REST is a strong default for resource-oriented APIs with HTTP caching and conventional tooling.
GraphQL is useful when clients need different nested response shapes, but requires query-cost
limits, field-level authorization, caching decisions, and protection from N+1 queries.

## Docker and Kubernetes deployment

Local container:

```bash
API_TOKEN=interview-demo-token docker compose -f docker-compose.legacy.yml up --build
```

Cluster deployment (replace the image and secret for your registry/environment):

```bash
docker build -t REGISTRY/api-interview-lab:0.2.0 .
docker push REGISTRY/api-interview-lab:0.2.0
kubectl create namespace api-interview
kubectl -n api-interview create secret generic api-interview-lab-secrets \
  --from-literal=API_TOKEN='replace-me'
kubectl apply -f deploy/k8s/
kubectl -n api-interview set image deployment/api-interview-lab \
  api=REGISTRY/api-interview-lab:0.2.0
kubectl -n api-interview port-forward service/api-interview-lab 8000:80
```

The manifests demonstrate rolling updates, two replicas, startup/readiness/liveness probes,
CPU/memory budgets, a HorizontalPodAutoscaler, a PodDisruptionBudget, non-root execution, a
ConfigMap, and a Secret reference. HPA requires Metrics Server.

SQLite is only for local simulation. Multiple pods cannot safely share its local file. A real
deployment should use managed PostgreSQL/MySQL, migrations as a separate job, immutable image
tags, Ingress/Gateway with TLS, NetworkPolicy, and an external secret manager.

## Observability

The service exposes:

- `/health/live`: process health; Kubernetes restarts it on repeated failure.
- `/health/ready`: database dependency health; unhealthy pods leave Service endpoints.
- `/metrics`: Prometheus counters, in-flight requests, and latency histograms.
- `X-Request-ID`: accepted/generated on each request and returned to the caller.
- JSON logs on stdout for collection by Fluent Bit, Vector, or another agent.

If the Prometheus Operator is installed, apply
`deploy/observability/servicemonitor.yaml`. Build Grafana panels and alerts around request rate,
5xx rate, p95/p99 latency, saturation, readiness, and pod restarts. In production, add
OpenTelemetry SDK/Collector instrumentation and export traces to Jaeger, Tempo, Datadog, or
another backend; propagate trace context to downstream services.

## Reliability discussion points

- Use connect/read/write/pool deadlines; retry only transient and idempotent operations with
  exponential backoff plus jitter.
- Limit concurrency and rate, honor `Retry-After`, and use circuit breaking for sustained
  downstream failure.
- Define whether batch extraction fails fast, returns partial results, or dead-letters failures.
- Prefer cursor/keyset pagination at scale; offset pagination can skip/duplicate records during
  concurrent writes and becomes expensive at large offsets.
- Use idempotency keys for retryable creates and conditional requests/ETags for concurrency.

For rapid revision, see [`docs/INTERVIEW_CHEATSHEET.md`](INTERVIEW_CHEATSHEET.md). For design
decisions, see
[`ai_skills/api-interview-guide/PROJECT_KNOWLEDGE.md`](../ai_skills/api-interview-guide/PROJECT_KNOWLEDGE.md).
