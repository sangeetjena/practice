# ObserveAgent

Standalone incident investigation lab at `practice/ObserveAgent`, alongside `practice/API`.

Start with [the complete configuration and workflow walkthrough](docs/CONFIGURATION.md).
It maps every embedding, RAG, LangGraph, tool and feedback step to the implementation.

## Start

From this directory:

```powershell
python -m pip install -e ".[dev]"
$env:PROMETHEUS_URL = "http://localhost:9090"
python -m observe_agent.api
```

Open http://localhost:8090/docs. POST `data/sample-incident.json` to `/v1/incidents`.
The response includes `report`, `status`, `proposed_actions`, and `action_results`.

Default: ChromaDB vector storage, hash embeddings and offline rule reasoning.
Enable `EMBEDDING_PROVIDER=openai` and `LLM_PROVIDER=openai` with model names and API keys
for semantic embeddings and LLM reasoning. See `.env.example` and the configuration guide.

LangGraph controls feature extraction, retrieval, diagnosis, approval, execution and reflection.
Diagnostic responses feed a second diagnosis. Reviewed resolutions become new Chroma knowledge.
Tools support HTTPS GET, SMTP email and opening a PR for an existing branch. Actions default to
dry-run and need configured targets plus approval. The separate
[Spark workflow](docs/SPARK_WORKFLOW.md) can inspect a catalog-mapped JSON configuration,
prepare a bounded memory patch and create a branch plus draft PR after approval.

Run `python -m observe_agent reindex` after changing embedding configuration.
Run `python -m pytest` and `ruff check .` to validate.
The API stack's `../API/docker-compose.yml` builds this sibling project's Dockerfile.

Prometheus holds metrics; Jaeger holds traces; API logs remain on container stdout.
This agent currently queries metrics and explicitly configured diagnostic APIs.
