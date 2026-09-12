# Spark incident to reviewed configuration PR

`observe_agent/spark.py` provides a separate LangGraph subworkflow for the Spark example.
It is a Python integration API, not a new HTTP endpoint. `data/job-catalog.json` is a template;
replace its example repository and configuration path with your actual job mapping.

## What makes it find the repository?

The catalog maps an exact job ID to tenant, repository, JSON configuration path, owner and memory
budget. An incident collector provides the deployed commit and effective settings. Chroma retrieval
can suggest a historical resolution, but catalog lookup determines where the job lives.

## Run the workflow

```python
import os
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from observe_agent.spark import GitHubRepository, build_spark_graph

repository = GitHubRepository(os.environ["GITHUB_TOKEN"], ["your-org/data-pipelines"])
checkpoints = SqliteSaver(sqlite3.connect("spark.checkpoints.db", check_same_thread=False))
graph = build_spark_graph("data/job-catalog.json", repository, checkpoints, execute=False)
config = {"configurable": {"thread_id": "spark-incident-001"}}
result = graph.invoke(
    {
        "incident_id": "spark-incident-001",
        "tenant_id": "acme",
        "job_id": "daily-orders-etl",
        "deployed_commit": "FULL_40_CHARACTER_DEPLOYED_COMMIT_SHA",
        "evidence": {
            "executor_heap_oom": True,
            "skew_ruled_out": True,
            "overrides_ruled_out": True,
            "effective_executor_memory": "4g",
            "proposed_executor_memory": "8g",
        },
    },
    config,
)
print(result)  # Review the actual diff and evidence before resuming.
result = graph.invoke(Command(resume={"approved": True, "reviewer": "service-owner"}), config)
```

The values above illustrate the contract; do not assert evidence flags without verifying them.
Run with `execute=False` first. With `execute=True`, approval creates the branch, commits the exact
JSON update and opens a draft PR. It does not merge, deploy or send email. The main incident graph's
existing email tool remains separate.

## Nodes and decisions

1. Discover: exact catalog lookup and tenant check.
2. Inspect: GitHub read at the deployed commit, restricted to the catalog configuration path.
3. Propose: check heap-OOM evidence, ruled-out skew/overrides, effective/source match and memory budget.
4. Review: show the complete proposed diff through a LangGraph interrupt.
5. Publish: ensure target branch still equals the inspected deployed commit; create a draft PR.

Missing evidence yields `needs_evidence`. Configuration mismatch yields `configuration_drift`.
An invalid or over-budget memory change fails validation. An existing remediation branch causes
publication to stop rather than overwrite it. Inspect that branch after an ambiguous network failure.

## Limits and reasoning challenges

This subworkflow supports a flat JSON map containing `spark.executor.memory`, expressed in whole
GiB. It does not edit arbitrary Python, Helm or Airflow code. It validates configuration structure
and policy; a Spark cluster canary is still needed to validate runtime recovery and capacity.

The runtime evidence currently comes from an operator or upstream collector. This module does not
claim to diagnose heap OOM from raw Spark logs or automatically distinguish every OOM cause.
The main RAG/LLM report can inform the operator's proposal; the Spark patcher is deterministic and
does not copy a retrieved recommendation into production without review. Keep the resolution,
actual before/after values, deployed/fix commits, and recovery measurements in reviewed feedback.
