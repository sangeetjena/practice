# ObserveAgent project guidance

Read README.md, docs/CONFIGURATION.md and docs/SPARK_WORKFLOW.md before changing this subsystem.
For cloud/multi-tenant changes read PROJECT_KNOWLEDGE.md, docs/CLOUD_RUNTIME.md,
docs/MODULE_GUIDE.md and docs/GOOGLE_CLOUD.md. Install .[cloud,dev] before testing.
It is a sibling of API and has independent dependencies, tests and packaging.
Run `ruff check .` and `pytest` from this directory after changes.
Keep Chroma serving retrieval separate from audit and graph checkpoints. The lab uses SQLite;
the cloud runtime requires PostgreSQL and remote Chroma. Never publish the lab API as multi-tenant.
Do not describe hash embeddings as semantic models, hypotheses as confirmed causes, or reviewed
knowledge updates as model training. Preserve tenant filters and approval boundaries.
Spark remediation supports only catalog-scoped flat JSON executor-memory changes. New config
formats need parsers, evidence gates and tests; do not use unrestricted shell commands as tools.
