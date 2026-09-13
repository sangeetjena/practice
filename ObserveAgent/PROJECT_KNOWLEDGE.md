# ObserveAgent project knowledge

There are two explicit execution profiles. `observe_agent.api` is the original synchronous,
unauthenticated localhost teaching lab (SQLite and embedded Chroma). `observe_agent.cloud.api` is
the authenticated asynchronous runtime (PostgreSQL and remote Chroma). Dockerfile.cloud and
compose.cloud.yml build the latter. Never conflate their deployment or security properties.

## Cloud invariants

- Customer identity comes from a server-managed SHA-256 API-key registry. Tenant and reviewer
  request-body fields are rejected. Signed Google OIDC tokens separately authenticate internal
  Pub/Sub and Scheduler requests with exact audience/service-account checks.
- All public incident, message and report access filters `(tenant_id, incident_id)`.
- Each incident has a stable opaque session ID. Each investigation revision has an opaque run ID,
  used as its LangGraph thread. New evidence preserves session history, starts a new run, and
  invalidates prior proposal approval. Approval resumes the same run, never a caller-chosen thread.
- Incident creation and event insertion share one SQL transaction. Publication may duplicate;
  worker processing deduplicates persisted event IDs and uses a PostgreSQL session advisory lock
  to exclude simultaneous graph execution for one tenant/incident.
- Completion and event ACK eligibility commit together. Failed work retries five attempts then
  becomes a durable dead event. Dead events are ACKed to stop endless model calls.
- At most one event per incident is active. Concurrent new inputs return 409; idempotent repeats
  return the existing state. This is intentional admission control, not silent input loss.
- Remote Chroma collections are separate per tenant and embedding profile. PostgreSQL active
  archive IDs fence stale index entries. Reindex explicitly repairs partial publication or models.
- Side effects have durable reservations. A crash with an unknown external outcome does not
  trigger an automatic second PR/email. Reconcile externally and create a newly reviewed proposal.

## Scope and limitations

This is a runnable reference implementation, not a production SLA claim. API-key authentication
is implemented; federated customer OIDC, per-user incident ACLs, automated tenant deletion,
encrypted artifact archives, per-tenant spend quotas and memory summarization are extensions.
Tenant membership currently grants role-based access to that tenant's incidents. The runtime
requires tenant-scoped Prometheus endpoints and server-managed service ownership configuration.
Shared service-only metrics cannot be converted into private customer metrics by a prompt.

Spark remediation remains a separate Python LangGraph workflow, with catalog-scoped flat JSON
memory changes and operator-supplied runtime evidence. The cloud REST API does not automatically
dispatch incidents to Spark remediation. Models still do not freely select arbitrary tools.

See docs/MODULE_GUIDE.md for every Python module and example. CI tests PostgreSQL advisory locks
and durable graph restoration when TEST_POSTGRES_URL is set; SQLite tests cannot prove those.
