# Day 1 — Learn by running the system

All times IST. Use Python; keep the exercises small enough to explain without notes.

| Time | Exercise | Evidence |
|---|---|---|
| 08:00–08:30 | Read README and system design | Describe client, gateway, services and telemetry |
| 08:30–10:00 | Read app/auth/store; follow pagination and idempotency | Explain cursor context and duplicate-write race |
| 10:00–10:15 | Recruiter slot / break | |
| 10:15–11:30 | Start Compose; call all services; switch tenants/auth methods | Same IDs resolve tenant-specific records |
| 11:30–11:45 | Break | |
| 11:45–13:00 | Run platform_patterns.py; inspect pooled async client | Results arrive in completion order; retries are bounded |
| 13:00–13:15 | Recruiter slot / break | |
| 13:15–14:00 | Lunch | |
| 14:00–15:15 | Trace orders → customers; inspect RED dashboard and logs | One trace joins both services |
| 15:15–15:30 | Break | |
| 15:30–16:45 | Inject delay, failure, collector outage | Diagnose 504/502 and best-effort telemetry |
| 16:45–17:30 | Submit an import job; restart worker; check result | Durable accepted work, idempotent effects |
| 17:30–18:30 | Dinner/family break | |
| 18:30–19:15 | Run tests/governance; inspect Kubernetes manifests | Explain failure paths and scaling assumptions |
| 19:15–20:00 | 35-minute design mock + 10-minute review | Identify three gaps, then stop |

## Exercise: async job lifecycle

In orders Swagger, POST `/api/v1/import-jobs` with an Idempotency-Key and:

```json
{"orders":[{"name":"Import example","customer_id":"customers-001","product_id":"products-001","quantity":1,"unit_price":10}]}
```

The 202 response includes a job ID. Poll GET `/api/v1/jobs/{job_id}`. The separate worker claims
pending rows with an atomic conditional update and a 60-second lease, then creates orders with
per-job/per-item idempotency keys. Job states: pending → processing → succeeded, with database
operation failures returning to pending for retry or failed after three handled failures.
If a worker dies mid-job, another worker can reclaim the expired lease. Committed effects are
reused on retry. A stale worker cannot overwrite a newer claim's result. This is at-least-once
execution with idempotent effects, not blanket exactly-once delivery.

This small worker does not implement lease renewal, fairness, queue-depth metrics or an external
broker. Imports are capped at 100 records. For long jobs renew leases, add per-tenant scheduling,
backoff/dead-letter operations and queue telemetry. At higher scale publish through a transactional
outbox to a durable broker; do not introduce an unprotected DB/queue dual write.

## Check yourself

1. Why does a tenant header fail to change authorization?
2. Can you reuse an acme cursor with a globex credential? Why not?
3. What happens if a POST succeeds but the HTTP response is lost?
4. Why doesn't retrying POST blindly solve the problem?
5. Why can p99 not be averaged across pods?
6. Does a healthy liveness probe prove PostgreSQL is reachable?
7. Can a running collector guarantee that every metric or trace is delivered?
8. Why is a static OpenAPI catalog different from observed network discovery?
9. What creates additional replicas: the LB, HPA or Kubernetes Service?
10. How can one tenant exhaust a shared database pool even with correct row filtering?
