# Commerce API Platform — Day 1 interview lab

Three small independently runnable services: **orders, customers, products**. Each serves 15
paginated sample records per tenant (`acme`, `globex`). Follow a request from an Nginx load
balancer through authentication, tenant-scoped SQL, metrics, logs, and a distributed trace.

This is a working learning lab, not a complete production platform. The original REST/GraphQL
and extraction examples remain available in [the legacy guide](docs/LEGACY.md).

## Start on Windows / Docker Desktop

Run from the `API` directory in PowerShell. Docker Desktop must be running with Linux containers.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python scripts/bootstrap.py
docker compose up --build -d
$env:DEMO_API_KEY = python scripts/credentials.py
curl.exe -H "X-API-Key: $env:DEMO_API_KEY" "http://localhost:8080/orders/api/v1/orders?limit=5"
python examples/platform_patterns.py
python scripts/discover.py
pytest
ruff check .
python scripts/governance.py
```

Bash differences: activate with `source .venv/bin/activate`, set the key with
`export DEMO_API_KEY=$(python scripts/credentials.py)`, and use `curl` instead of `curl.exe`.
The bootstrap command refuses to overwrite an existing `.env`; preserve its secrets between
restarts. Existing users should back up an old `.env` and generate the new format once.

| Local URL | Purpose |
|---|---|
| http://localhost:8080/orders/docs | Orders Swagger UI; click **Authorize**, select one method |
| http://localhost:8080/customers/docs | Customers API documentation |
| http://localhost:8080/products/docs | Products API documentation |
| http://localhost:8080/orders/api/v1/catalog | Authenticated API catalog |
| http://localhost:16686 | Jaeger distributed traces; select `orders` service |
| http://localhost:9090 | Prometheus queries and alert-rule state |
| http://localhost:3000 | Grafana: user `admin`; password is local `.env` POSTGRES_PASSWORD |

Ports bind to localhost. Backend/database/collector ports are not published. One Uvicorn worker
runs per container so Prometheus metrics remain process-correct. Scale containers, not workers.

## Services and API contracts

| Service | List | Detail | Extra capability |
|---|---|---|---|
| orders | `/orders/api/v1/orders?limit=5` | `/orders/api/v1/orders/{id}` | Idempotent POST; `/{id}/customer` traces a downstream call |
| customers | `/customers/api/v1/customers?limit=5` | `/customers/api/v1/customers/{id}` | Configurable delay/503 for failure exercises |
| products | `/products/api/v1/products?limit=5` | `/products/api/v1/products/{id}` | Product samples and prices |

Gateway strips the first service prefix. Direct service URLs start at `/api/v1/...`.
Every service also has `/docs`, `/openapi.json`, `/health/live`, `/health/ready`, and internal
`/metrics`. ROOT_PATH makes generated Swagger URLs work behind the gateway.

List returns `items` and `next_cursor`; pass the cursor unchanged on the next request. Limit is
1–100; cursor is signed and bound to tenant and service. Keyset ordering is by ID, not creation
time. It avoids offset scans, but **does not promise a snapshot across concurrent inserts**.

## Authentication and tenants

Use exactly one method per request:

```powershell
# API key
$env:DEMO_API_KEY = python scripts/credentials.py --tenant acme
curl.exe -H "X-API-Key: $env:DEMO_API_KEY" http://localhost:8080/orders/api/v1/orders
# Basic (local learning; use TLS outside localhost)
$password = python scripts/credentials.py --tenant acme --kind password
curl.exe -u "acme:$password" http://localhost:8080/customers/api/v1/customers
# Signed short-lived JWT; local issuer helper only
$token = python scripts/mint_token.py --tenant globex
curl.exe -H "Authorization: Bearer $token" http://localhost:8080/products/api/v1/products
```

Tenant comes from the credential mapping or verified JWT claim, never `X-Tenant-ID` or body
input. Reads require `read`; order creation requires `write`. Invalid credentials are 401,
insufficient scopes 403, missing/other-tenant records 404. JWT checks algorithm, signature,
issuer, audience, required claims, and expiry. Idempotency keys and SQL primary keys are scoped
by tenant. The two sample tenants intentionally reuse IDs to demonstrate filtering.

The lab's Basic/API-key mapping contains plaintext secrets in ignored local configuration.
JWT uses a shared HMAC key, not a full OAuth/OIDC provider. Production: use IdP/JWKS asymmetric
verification, workload identity, scoped downstream delegation, secret rotation and hashed
API-key storage. Shared HMAC means every holder can mint tokens; do not use this trust model
across independent production organizations. Identity forwarding is only to a fixed trusted
customer-service URL. Internal HTTP clients explicitly ignore ambient proxy variables.

## Create and retry an order

In Swagger select POST `/api/v1/orders`, provide `Idempotency-Key: interview-1`, then:

```json
{"name":"Interview order","customer_id":"customers-001","product_id":"products-001","quantity":2,"unit_price":10}
```

Repeat the same request/key: same resource and 201 result. Change quantity using the same key:
409. Concurrent requests across replicas share PostgreSQL's uniqueness constraint and atomic
transaction. Keys persist in this demo; production needs retention and published retry windows.
The create example validates reference formats but does not perform referential validation
against other services or implement real checkout/payment workflows. Monetary floats are demo
values; real billing needs decimal/minor-unit arithmetic.

## Monitoring and troubleshooting exercise

```powershell
curl.exe -H "X-API-Key: $env:DEMO_API_KEY" http://localhost:8080/orders/api/v1/orders/orders-001/customer
$env:CUSTOMERS_DELAY_MS = '1000'
docker compose up -d customers
# Repeat the request; find the slow child span in Jaeger.
$env:CUSTOMERS_DELAY_MS = '3000'
docker compose up -d customers
# Orders now returns 504 after its 2s dependency timeout.
$env:CUSTOMERS_DELAY_MS = '0'
$env:CUSTOMERS_FAIL = 'true'
docker compose up -d customers
# Customer returns 503; orders translates dependency failure to 502.
$env:CUSTOMERS_FAIL = 'false'
docker compose up -d customers
docker compose logs --tail=50 orders customers
```

Logs contain normalized route, status, duration, request ID, and trace ID; no credentials or
payloads. OpenTelemetry exports through a bounded batch processor and Collector to Jaeger.
Prometheus scrapes every discovered replica. Grafana provisions RED panels. Alert expressions
are evaluated in Prometheus; an external Alertmanager and notification routes are **not** wired.
Jaeger and monitoring storage are ephemeral lab defaults. Prometheus rules require sustained
traffic/window duration; one request will not immediately create a meaningful p95 chart.

Try `docker compose stop otel`: API traffic still works; trace export can fail/drop after bounded
buffers fill. Restart with `docker compose start otel`. Collection is best-effort, not an
exactly-once audit system. No raw packet/eBPF discovery is implemented: the discovery script
combines a trusted declared catalog, live OpenAPI and readiness. Metrics show observed routes.

## Scale and deploy

```powershell
docker compose up -d --scale orders=3 --scale customers=2
```

Nginx uses Docker DNS with a 10-second refresh to resolve current replicas. Gateway throttling
is **per IP and per gateway replica**, not a distributed tenant quota. Fixed host ports are only
on the gateway/monitoring UIs so app replicas do not conflict.

For a Linux VM, use the same Compose stack, persistent PostgreSQL backups, and a managed TLS
proxy/load balancer in front of the private gateway. Keep dashboards private. A single VM is
not highly available. For Kubernetes, see [deployment instructions](docs/DEPLOYMENT.md).

## Project map and study sequence

- `platform/app.py`: HTTP contracts, error mapping, scope checks, downstream call.
- `platform/auth.py`: API key, Basic and JWT strategies yielding one Principal.
- `platform/store.py`: tenant-scoped SQL and atomic idempotency.
- `platform/telemetry.py`: RED metrics, JSON logs and OpenTelemetry instrumentation.
- `platform/client.py`: pooled async transport, bounded retries/concurrency and pagination.
- `scripts/discover.py`, `scripts/governance.py`: discovery and executable API rules.
- `deploy/platform/`: gateway, Collector, Prometheus, Grafana and Kubernetes examples.
- [Full system design](docs/SYSTEM_DESIGN.md): requirements → estimation → HLD → trade-offs.
- [Day 1 exercises](docs/DAY1_LAB.md): hands-on itinerary and acceptance checks.

Use `python scripts/governance.py` and `pytest` as release gates. The included GitHub Actions
workflow runs lint/tests/governance, boots Compose, and runs the live smoke script on API PRs.
The worker also supports POST `/orders/api/v1/import-jobs` and GET `/orders/api/v1/jobs/{job_id}`;
see the Day 1 lab for the request body and crash-recovery exercise.
