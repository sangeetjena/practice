# API Interview Cheatsheet

## Thirty-second answer

“I separate transport contracts, domain objects, and persistence behind a repository. FastAPI
provides OpenAPI and boundary validation through Pydantic. REST fits stable resource-oriented
operations; GraphQL fits clients needing different response shapes. For fan-out HTTP reads, I
use bounded asyncio concurrency, deadlines, and an explicit failure policy. The app is packaged
as a non-root container and deployed with readiness/liveness probes and resource limits.”

## Rapid decisions

- Public CRUD API: REST first.
- Internal low-latency typed RPC: consider gRPC.
- Client-selected nested read graph: GraphQL.
- Server-to-client real-time updates: SSE; bidirectional: WebSocket.
- Fire-and-forget durable workflow: broker/event log, not synchronous HTTP.
- Trusted in-process record: dataclass.
- Untrusted input/output boundary: Pydantic.
- Local bounded analytics: pandas.
- I/O fan-out: asyncio with concurrency limits.
- CPU-bound Python work: processes, native/vectorized code, or distributed compute.

## Async failure choices

| Requirement | Mechanism |
|---|---|
| Preserve request order | `asyncio.gather()` |
| Process fastest response first | `asyncio.as_completed()` |
| Return results incrementally | async generator + `yield` |
| Limit in-flight operations | `asyncio.Semaphore` |
| Cancel siblings on structured failure | `asyncio.TaskGroup` |
| Keep individual failures as values | `gather(..., return_exceptions=True)` with care |

## Production gaps to volunteer

AuthN/AuthZ, idempotency, cursor pagination, rate limiting, caching, distributed tracing,
structured logs, metrics/SLOs, circuit breaking, schema migrations, external database, secret
management, autoscaling, ingress/TLS, and CI/CD security scanning.

## Client extraction choices

| Need | Choice |
|---|---|
| Raw JSON with editor/static-checker help | `TypedDict` |
| Lightweight trusted internal object | dataclass |
| Validate untrusted API JSON | Pydantic |
| Aggregate bounded tabular results | pandas |
| Concurrent page or endpoint retrieval | `httpx.AsyncClient` + asyncio |

Keep HTTP concerns in one client: base URL, default/custom headers, auth strategy, deadlines,
status handling, pagination, concurrency limits, and lifecycle. Transform its response afterward.

## Operations answer

Expose separate liveness and dependency-aware readiness probes. Emit RED metrics (request rate,
errors, duration) to Prometheus, structured logs to stdout, request/trace IDs across calls, and
OpenTelemetry traces through a Collector. Alert on SLO symptoms rather than isolated CPU spikes.
