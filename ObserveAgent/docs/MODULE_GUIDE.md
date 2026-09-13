# Code explanation and examples for every module

Read this beside the source. Cloud runtime modules also have individual pages under `modules/`.
Paths in the first column are relative to `observe_agent/` unless otherwise stated.

## Cloud request and execution modules

| Module | What it does | Worked example | Failure boundary |
|---|---|---|---|
| cloud/contracts.py | Validates public bodies and forbids unknown identity fields | IncidentInput accepts service=orders; tenant_id in the body is rejected | 422 before persistence |
| cloud/security.py | Hashes API credential, resolves principal, checks roles | Acme key resolves to Acme/alice/read-submit-review | 401 invalid key; 403 wrong role |
| cloud/config.py | Loads PostgreSQL, tenant, Chroma and delivery configuration | Tenant acme maps to its configured metrics endpoint | Startup fails for missing required configuration |
| cloud/database.py | Stores incidents, messages, outbox, records and proposal versions | submit writes inc-1 plus E1 atomically; append M1 advances revision | Conflict on stale state; advisory lock excludes simultaneous workers |
| cloud/knowledge.py | Archives tenant documents and searches remote Chroma | Acme's reviewed memory fix is searchable only in Acme's collection | Wrong tenant rejected; old profile needs reindex |
| cloud/effects.py | Reserves external actions before making a call | A replay after an uncertain SMTP outcome stops for reconciliation | Does not claim exactly-once external execution |
| cloud/runtime.py | Builds tenant dependencies and processes durable events | E1 starts R1; approval E2 resumes the saved R1 interrupt | Checkpoints survive process restart; five failed attempts become dead |
| cloud/transport.py | Verifies Google service identity, decodes event IDs, publishes outbox | Scheduler publishes E1; Pub/Sub pushes E1 with its own OIDC identity | Wrong audience/account rejected; failed publish leaves outbox eligible |
| cloud/api.py | Exposes authenticated async API or private worker endpoints | POST returns 202; GET polls state; message POST creates a new run | No background task is hidden after HTTP return |
| cloud/admin.py | Runs initialization, reindex and local queue-drain commands | python -m observe_agent.cloud.admin drain | Operator command; not exposed to customers |
| cloud/__init__.py | Declares the cloud runtime package | import observe_agent.cloud | No side effects |

## Shared graph, RAG and teaching modules

| Module | What it does | Worked example |
|---|---|---|
| models.py | Internal Pydantic incident, feature, report, action and feedback contracts | IncidentFeatures retains current value, baseline and exact query |
| config.py | Shared model and action environment settings | LLM_PROVIDER=openai selects the structured reasoner |
| providers.py | Builds configured embedder/reasoner adapters | hash/rule needs no remote model credentials |
| telemetry.py | Performs bounded read-only Prometheus queries | request-rate query is evaluated at incident start |
| features.py | Computes current/baseline/delta features and missing-evidence flags | p95=0.9, baseline=0.2 gives delta=0.7 |
| knowledge.py | Markdown chunking, hash/OpenAI embeddings and legacy SQLite archive | A runbook heading becomes a chunk; OpenAIEmbedding.embed returns its vector |
| vector_store.py | Legacy local Chroma serving adapter | Replacing a source makes old archive IDs ineligible for retrieval |
| reasoner.py | Rule baseline and schema-constrained OpenAI Responses diagnosis | Retrieved source IDs are the only permitted output citations |
| actions.py | Plans configured diagnostic/email/PR tools and checks policy | An allowed diagnostic_url becomes a proposal; dry_run does not send |
| agent.py | Builds actual LangGraph nodes, interrupts, reflection and feedback | Successful diagnostic body feeds one additional diagnosis |
| spark.py | Separate Spark catalog/configuration patch subworkflow | 4g to 8g JSON patch pauses before draft PR publication |
| api.py | Original synchronous localhost API | POST /v1/incidents waits for the report or approval interrupt |
| cli.py | Legacy ingestion, incident, feedback and reindex commands | python -m observe_agent ingest data/runbooks/commerce-latency.md |
| __main__.py | Dispatches the legacy CLI | python -m observe_agent --help |
| __init__.py | Package identity | import observe_agent |

The cloud runtime reuses `ReflexionAgent` with different storage/checkpointer adapters. It does not
use the legacy SQLite store or accept a public caller's tenant_id. Shared action planning is
deterministic; the LLM does not independently choose unrestricted tools.

## Scripts and deployment code

| File | What it does | Example |
|---|---|---|
| scripts/bootstrap_cloud.py | Generates ignored local credentials and Compose environment | Run once; existing secrets are preserved |
| scripts/cloud_example.py | Submits a customer incident and prints polling location | Set OBSERVE_API_URL and OBSERVE_API_KEY |
| Dockerfile.cloud | Packages cloud extras and listens on PORT | docker build -f Dockerfile.cloud -t observe-cloud . |
| compose.cloud.yml | Starts PostgreSQL, Chroma, migrations and API for local async practice | Use admin drain instead of Pub/Sub |
| deploy/gcp/cloudbuild.yaml | Builds and pushes the reviewed image | gcloud builds submit with _IMAGE substitution |
| deploy/gcp/deploy.sh | Deploys private Cloud Run API/worker, migration job and authenticated delivery | Supply existing Cloud SQL/Chroma/Secret Manager prerequisites |

## Tests as executable examples

`test_cloud.py` covers authentication, tenant boundaries, idempotency, message memory, approvals,
outbox failures and vector isolation without Google credentials. `test_cloud_postgres.py` proves
real PostgreSQL lock exclusion and checkpoint restoration in CI. Other test files show feature
ETL, retrieval versions, model adapters, human feedback, action policies and Spark patch review.
Run `pip install -e '.[cloud,dev]'`, then `ruff check .` and `pytest`.
