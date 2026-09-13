# Deploy ObserveAgent on Google Cloud

This path keeps LangGraph and FastAPI. It does not rewrite the agent in Google ADK. Google hosting
does not switch the model provider automatically. Default deployment is hash/rule/dry-run.

## Prerequisites you supply

- Google Cloud project, billing, deployment permissions, gcloud and Docker/Cloud Build access.
- Artifact Registry repository for the image.
- Cloud SQL PostgreSQL database and application credentials. Use a dedicated database/user.
- A private Chroma server reachable from Cloud Run, with durable storage and backups. The script
  does not provision Chroma or pretend embedded Chroma is Cloud Run persistence.
- Secret Manager secrets holding DATABASE_URL, OBSERVE_AUTH_KEYS and OBSERVE_TENANTS.
- A VPC connector when required to reach the private Chroma/Prometheus endpoints.

DATABASE_URL uses SQLAlchemy's driver prefix, for example:
`postgresql+psycopg://USER:PASSWORD@/observer?host=/cloudsql/PROJECT:REGION:INSTANCE`.
URL-encode special characters in credentials. The checkpoint adapter converts the prefix to the
psycopg-compatible `postgresql://` form while retaining the socket host. Do not put this value in git.

OBSERVE_AUTH_KEYS is a JSON array of SHA-256 credential hashes, tenant IDs, subjects and roles.
OBSERVE_TENANTS maps tenant IDs to owned services, scoped Prometheus URL and tool allowlists. See
.env.cloud.example. A customer cannot override those mappings through request parameters.

## Build and deploy

Run these from ObserveAgent in Bash, Cloud Shell, or WSL:

```bash
gcloud builds submit --config deploy/gcp/cloudbuild.yaml \
  --substitutions _IMAGE=REGION-docker.pkg.dev/PROJECT/REPOSITORY/observe-agent:VERSION

export PROJECT_ID=your-project
export REGION=your-region
export IMAGE=REGION-docker.pkg.dev/PROJECT/REPOSITORY/observe-agent:VERSION
export CLOUD_SQL_CONNECTION=PROJECT:REGION:INSTANCE
export DATABASE_SECRET=observe-database-url
export AUTH_SECRET=observe-auth-registry
export TENANTS_SECRET=observe-tenant-registry
export CHROMA_HOST=your-private-chroma-host
export VPC_CONNECTOR=your-connector
bash deploy/gcp/deploy.sh
```

The script enables APIs, creates four service accounts, assigns scoped invocation/publication
permissions, deploys a migration job, runs schema setup, deploys private API/worker services, creates
authenticated Pub/Sub push delivery and schedules the outbox publisher. It creates billable
resources when you run it. It has not been executed against your Google account by this task.

## Credentials and endpoint access

API and worker have Cloud SQL client permission. API can read the authentication registry secret;
worker does not receive customer API keys. Both read the tenant registry. Pub/Sub and Scheduler use
separate service accounts, exact audiences and worker invocation permissions. Application checks
the OIDC account too, so Scheduler cannot invoke the event endpoint as the push identity.

The API service is private. Grant `roles/run.invoker` to your trusted gateway or authorized test
identity. For an authorized gcloud user testing the private endpoint, send its Google ID token in
Authorization and the product credential in X-API-Key. IAM invocation and customer tenancy are
separate controls. Do not allow unauthenticated invocation of the worker.

## Model and vector configuration

Grant the worker accessor permission for your model-key secret, then attach it as LLM_API_KEY and/or
EMBEDDING_API_KEY with `gcloud run services update --update-secrets`. Set LLM_PROVIDER,
LLM_MODEL, EMBEDDING_PROVIDER and EMBEDDING_MODEL on the worker. The ingestion API needs no model
credentials. Use CHROMA_PORT, CHROMA_SSL and CHROMA_HEADERS for your server/gateway configuration.
If CHROMA_HEADERS contains a credential, inject it from Secret Manager as well.

The example script starts with plain internal Chroma port 8000. Change its deployment environment
for TLS or a different port before directing it at such an endpoint. Keep Chroma unreachable from
untrusted clients: this runtime's tenant-scoped adapter is its authorization boundary.

## Migrations, maintenance and scale

`python -m observe_agent.cloud.admin migrate` creates the current SQL tables and LangGraph schema.
It is idempotent initialization, not a general automatic migration of old SQLite files. Existing
lab data is not silently copied. Re-ingest reviewed source documents into the appropriate tenant.
Future schema alterations need explicit versioned migrations.

`python -m observe_agent.cloud.admin reindex --tenant acme` rebuilds only that tenant's active
source embeddings using the configured model and repairs missing Chroma rows. Run it as an
operator-controlled job, not as an unauthenticated customer endpoint.

The worker uses one request per instance and at most five instances in the example. Each worker
holds an advisory-lock connection plus graph/database connections. Budget PostgreSQL connections
before raising instance limits. Pub/Sub's 600-second ACK deadline and the worker's 600-second HTTP
timeout bound each request; external model calls have a 30-second timeout without hidden SDK retries.
Very large/long investigations should be split into smaller durable graph tasks.

Monitor queue age, failed/dead events, approval age, model latency/token usage, Chroma errors, SQL
connections and post-action recovery. This project records state and sanitized failure classes;
it does not yet export a full agent-specific metrics dashboard or enforce per-tenant spend quotas.

## Google references

- [Cloud Run container contract](https://docs.cloud.google.com/run/docs/container-contract)
- [Authenticated Pub/Sub push](https://docs.cloud.google.com/pubsub/docs/authenticate-push-subscriptions)
- [Pub/Sub ACK behavior](https://docs.cloud.google.com/pubsub/docs/push)
