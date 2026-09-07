# API Interview Lab

A modular, runnable Python reference for API and data-extraction interviews. The same
sales-order domain is represented with dataclasses, Pydantic, pandas, concurrent `asyncio`
clients, REST, and GraphQL so the trade-offs are easy to compare.

## Quick start

```bash
cd API
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
python -m pip install -e '.[dev]'
python scripts/load_feed.py
uvicorn api_interview_lab.server.main:app --reload
```

Open:

- REST/OpenAPI: <http://localhost:8000/docs>
- GraphQL IDE: <http://localhost:8000/graphql>
- Health probes: <http://localhost:8000/health/live> and `/health/ready`

In a second terminal:

```bash
python examples/run_patterns.py
pytest
```

## What to study

| Pattern | Reference | Interview point |
|---|---|---|
| Dataclass | `patterns/dataclass_pattern.py` | Lightweight domain objects; no runtime validation |
| Pydantic | `patterns/pydantic_pattern.py` | Boundary validation, coercion, serialization, JSON Schema |
| pandas | `patterns/pandas_pattern.py` | Vectorized local analytics; avoid for request-by-request hot paths |
| asyncio | `client/async_client.py` | Concurrent I/O, ordering, streaming, limits, partial failure |
| REST | `server/routers/orders.py` | Resource-oriented HTTP, status codes, pagination |
| GraphQL | `server/graphql/schema.py` | Client-selected fields and one typed endpoint |

For the architecture, request flows, interview talking points, and extension rules, read
[`ai_skills/api-interview-guide/PROJECT_KNOWLEDGE.md`](ai_skills/api-interview-guide/PROJECT_KNOWLEDGE.md).

## REST examples

```bash
curl 'http://localhost:8000/api/v1/orders?page=1&page_size=5'
curl 'http://localhost:8000/api/v1/orders/ORD-1001'
curl -X POST 'http://localhost:8000/api/v1/orders' \
  -H 'Content-Type: application/json' \
  -d '{"id":"ORD-2001","customer_id":"CUS-99","product":"Keyboard","quantity":2,"unit_price":75.0,"status":"created"}'
```

## GraphQL example

```graphql
query {
  orders(limit: 3) {
    id
    product
    revenue
    status
  }
}
```

## Containers and Kubernetes

```bash
docker compose up --build
kubectl apply -f deploy/k8s/
kubectl port-forward service/api-interview-lab 8000:80
```

The Kubernetes sample includes ConfigMap-based configuration, non-root execution,
resource requests/limits, rolling updates, and liveness/readiness probes. SQLite is for
local simulation only; production deployments should use an external database.

