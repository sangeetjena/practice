"""Real PostgreSQL gates: session lock exclusion and graph resume after reconstruction.

CI supplies TEST_POSTGRES_URL. Local SQLite tests do not prove these guarantees.
"""

import os
import uuid
from contextlib import contextmanager

import chromadb
import pytest
from langgraph.checkpoint.postgres import PostgresSaver

from observe_agent.actions import ActionPlanner
from observe_agent.agent import ReflexionAgent
from observe_agent.cloud.database import Busy, Database, fingerprint
from observe_agent.cloud.effects import DurableActionExecutor
from observe_agent.cloud.knowledge import TenantKnowledge
from observe_agent.cloud.runtime import Worker
from observe_agent.config import Settings
from observe_agent.features import IncidentFeatureExtractor
from observe_agent.knowledge import HashEmbedding

URL = os.getenv("TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(
    not URL, reason="TEST_POSTGRES_URL is required for PostgreSQL integration"
)


def test_postgres_locks_and_restart_approval(tmp_path):
    db = Database(URL, initialize=True)
    other = Database(URL)
    tenant = "test-" + uuid.uuid4().hex[:12]
    with db.incident_lock(tenant, "i1"), pytest.raises(Busy), other.incident_lock(tenant, "i1"):
        pass
    checkpoint_url = URL.replace("postgresql+psycopg://", "postgresql://")
    with PostgresSaver.from_conn_string(checkpoint_url) as saver:
        saver.setup()

    class Metrics:
        def __init__(self):
            self.values = iter([100, 80, 0.08, 0.01, 0.9, 0.2])

        def instant_value(self, query, at):
            return next(self.values)

    class Factory:
        @contextmanager
        def open(self, scope):
            client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
            store = TenantKnowledge(db, client, HashEmbedding(), scope)
            settings = Settings(
                action_allowlist=("http_get",), http_allowed_hosts=("status.example.com",)
            )
            with PostgresSaver.from_conn_string(checkpoint_url) as saver:
                yield ReflexionAgent(
                    IncidentFeatureExtractor(Metrics()),
                    store,
                    action_planner=ActionPlanner(settings),
                    action_executor=DurableActionExecutor(settings, store),
                    checkpointer=saver,
                )

    payload = {
        "id": "i1",
        "title": "Slow orders",
        "service": "orders",
        "started_at": "2026-09-13T10:00:00Z",
        "environment": "production",
        "annotations": {},
        "action_context": {"diagnostic_url": "https://status.example.com/health"},
    }
    db.submit(tenant, "owner", payload, "key", fingerprint(payload))
    event = next(e for e in db.pending() if e["tenant_id"] == tenant)
    Worker(db, Factory()).process(event["id"])
    row = db.get(tenant, "i1")
    assert row["status"] == "awaiting_approval"
    ids = [a["id"] for a in row["result"]["proposed_actions"]]
    db.append(
        tenant,
        "i1",
        "owner",
        "approval",
        {
            "id": "approve",
            "approved": True,
            "proposal_version": row["proposal_version"],
            "action_ids": ids,
        },
    )
    event = next(e for e in db.pending() if e["tenant_id"] == tenant)
    # A fresh worker opens new PG connections and restores the graph's interrupt.
    Worker(other, Factory()).process(event["id"])
    assert db.get(tenant, "i1")["result"]["action_results"][0]["status"] == "dry_run"
    assert Worker(other, Factory()).process(event["id"]) == "done"
