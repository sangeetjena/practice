from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from observe_agent.spark import build_spark_graph


class Repository:
    def read(self, job, commit):
        return '{"spark.executor.memory":"4g"}', "blob"

    def publish(self, state):
        raise AssertionError("dry-run must not publish")


def test_spark_proposes_exact_patch_and_waits_for_approval():
    graph = build_spark_graph(
        Path(__file__).parents[1] / "data/job-catalog.json", Repository(), InMemorySaver()
    )
    config = {"configurable": {"thread_id": "spark-1"}}
    result = graph.invoke(
        {
            "incident_id": "spark-1",
            "tenant_id": "acme",
            "job_id": "daily-orders-etl",
            "deployed_commit": "a" * 40,
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
    assert result["__interrupt__"]
    assert '"8g"' in result["patch"]
    assert (
        graph.invoke(Command(resume={"approved": True, "reviewer": "sre"}), config)["status"]
        == "dry_run"
    )


def test_catalog_rejects_other_tenant():
    graph = build_spark_graph(
        Path(__file__).parents[1] / "data/job-catalog.json", Repository(), InMemorySaver()
    )
    with pytest.raises(ValueError, match="another tenant"):
        graph.invoke(
            {"job_id": "daily-orders-etl", "tenant_id": "other"},
            {"configurable": {"thread_id": "wrong"}},
        )
