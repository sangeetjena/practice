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

