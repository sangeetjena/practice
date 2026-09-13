"""Worked API/event tests: no model, Google account or real remediation required."""

import base64
import hashlib
import json
from contextlib import contextmanager

import chromadb
import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver

from observe_agent.agent import ReflexionAgent
from observe_agent.cloud.api import create_app
from observe_agent.cloud.config import CloudSettings
from observe_agent.cloud.database import Busy, Database
from observe_agent.cloud.knowledge import TenantKnowledge
from observe_agent.cloud.runtime import Worker
from observe_agent.cloud.transport import OutboxPublisher, decode_event
from observe_agent.features import IncidentFeatureExtractor
from observe_agent.knowledge import HashEmbedding


@pytest.fixture
def environment(tmp_path):
    keys = [
        {
            "sha256": hashlib.sha256(key.encode()).hexdigest(),
            "tenant_id": tenant,
            "subject": tenant + "-operator",
            "roles": roles,
        }
        for key, tenant, roles in [
            ("a-secret", "acme", ["read", "submit", "review"]),
            ("b-secret", "globex", ["read", "submit", "review"]),
            ("read-secret", "acme", ["read"]),
        ]
    ]
    url = f"sqlite:///{tmp_path / 'cloud.db'}"
    db = Database(url, initialize=True)
    settings = CloudSettings(
        url,
        "",
        json.dumps(keys),
        {
            tenant: {"services": ["orders"], "prometheus_url": "https://metrics.example"}
            for tenant in ["acme", "globex"]
        },
        "unused",
    )
    return db, settings


def submit(client, key="a-secret", incident_id="inc-1"):
    return client.post(
        "/v1/incidents",
        headers={"X-API-Key": key, "Idempotency-Key": incident_id},
        json={"id": incident_id, "title": "Slow orders", "service": "orders"},
    )


def test_authentication_tenant_scope_and_submission_idempotency(environment):
    db, settings = environment
    with TestClient(create_app(settings, db)) as client:
        assert client.get("/v1/incidents/inc-1").status_code == 401
        assert submit(client).status_code == 202
        assert submit(client).status_code == 202
        assert len(db.pending()) == 1
        assert (
            client.get("/v1/incidents/inc-1", headers={"X-API-Key": "b-secret"}).status_code == 404
        )
        assert submit(client, "b-secret").status_code == 202
        assert db.get("acme", "inc-1")["run_id"] != db.get("globex", "inc-1")["run_id"]
        assert submit(client, "read-secret", "inc-2").status_code == 403
        forged = client.post(
            "/v1/incidents",
            headers={"X-API-Key": "a-secret", "Idempotency-Key": "x"},
            json={"id": "new", "title": "fake", "service": "orders", "tenant_id": "globex"},
        )
        assert forged.status_code == 422
        changed = client.post(
            "/v1/incidents",
            headers={"X-API-Key": "a-secret", "Idempotency-Key": "inc-1"},
            json={"id": "inc-1", "title": "changed", "service": "orders"},
        )
        assert changed.status_code == 409


class Metrics:
    def instant_value(self, query, at):
        return 0.1


class Factory:
    def __init__(self, db, tmp_path):
        self.db = db
        self.client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
        self.saver = InMemorySaver()

    @contextmanager
    def open(self, tenant):
        knowledge = TenantKnowledge(self.db, self.client, HashEmbedding(), tenant)
        yield ReflexionAgent(
            IncidentFeatureExtractor(Metrics()), knowledge, checkpointer=self.saver
        )


def test_async_worker_replay_and_new_message_memory(environment, tmp_path):
    db, settings = environment
    factory = Factory(db, tmp_path)
    worker = Worker(db, factory)
    with TestClient(create_app(settings, db)) as client:
        submit(client)
        event = db.pending()[0]
        assert worker.process(event["id"]) == "done"
        assert worker.process(event["id"]) == "done"
        first = db.get("acme", "inc-1")
        response = client.post(
            "/v1/incidents/inc-1/messages",
            headers={"X-API-Key": "a-secret"},
            json={"id": "msg-1", "content": "Memory was reduced yesterday"},
        )
        assert response.status_code == 202
        assert response.json()["revision"] == 2
        assert response.json()["session_id"] == first["session_id"]
        event = db.pending()[0]
        worker.process(event["id"])
        second = db.get("acme", "inc-1")
        assert second["run_id"] != first["run_id"]
        incident = db.record_get("acme", "incident", second["run_id"])
        assert (
            "Memory was reduced yesterday" in incident["annotations"]["untrusted_session_context"]
        )
        assert (
            client.get(
                "/v1/incidents/inc-1/messages", headers={"X-API-Key": "b-secret"}
            ).status_code
            == 404
        )


def test_approval_version_and_reviewer_are_validated(environment):
    db, settings = environment
    with TestClient(create_app(settings, db)) as client:
        submit(client)
        event = db.pending()[0]
        db.finish(event, {"status": "awaiting_approval", "proposed_actions": [{"id": "a-1"}]})
        version = db.get("acme", "inc-1")["proposal_version"]
        path = "/v1/incidents/inc-1/actions/decision"
        body = {
            "id": "approval-1",
            "approved": True,
            "proposal_version": "stale",
            "action_ids": ["a-1"],
        }
        assert client.post(path, headers={"X-API-Key": "a-secret"}, json=body).status_code == 409
        body["proposal_version"] = version
        assert client.post(path, headers={"X-API-Key": "read-secret"}, json=body).status_code == 403
        assert (
            client.post(
                path, headers={"X-API-Key": "a-secret"}, json={**body, "reviewer": "fake"}
            ).status_code
            == 422
        )
        assert client.post(path, headers={"X-API-Key": "a-secret"}, json=body).status_code == 202
        assert client.post(path, headers={"X-API-Key": "a-secret"}, json=body).status_code == 202
        assert db.history("acme", "inc-1")[0]["subject"] == "acme-operator"


def test_outbox_publish_failure_does_not_lose_event(environment):
    db, settings = environment
    with TestClient(create_app(settings, db)) as client:
        submit(client)

    class FailedPublisher:
        def publish(self, topic, payload):
            raise RuntimeError("network down")

    with pytest.raises(RuntimeError):
        OutboxPublisher(db, "topic", FailedPublisher()).publish()
    assert len(db.pending()) == 1
    assert db.pending()[0]["published_at"] is None


def test_incident_lock_excludes_parallel_worker(environment):
    db, _ = environment
    with db.incident_lock("acme", "same"):
        with pytest.raises(Busy), db.incident_lock("acme", "same"):
            pass
        with db.incident_lock("globex", "same"):
            pass


def test_chroma_customer_memory_is_separated(environment, tmp_path):
    db, _ = environment
    client = chromadb.PersistentClient(path=str(tmp_path / "vectors"))
    acme = TenantKnowledge(db, client, HashEmbedding(), "acme")
    globex = TenantKnowledge(db, client, HashEmbedding(), "globex")
    acme.ingest(
        "fix",
        "# Resolution\nIncrease memory",
        {"tenant_scope": "acme", "service": "orders", "review_status": "approved"},
    )
    assert acme.search("memory", tenant_id="acme", service="orders")
    assert globex.search("memory", tenant_id="globex", service="orders") == []
    with pytest.raises(ValueError):
        acme.search("memory", tenant_id="globex", service="orders")


def test_queue_payload_accepts_only_valid_event_identifiers():
    raw = base64.b64encode(
        json.dumps({"event_id": "12345678-1234-1234-1234-123456789abc"}).encode()
    ).decode()
    assert decode_event({"message": {"data": raw}}) == "12345678-1234-1234-1234-123456789abc"
    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        decode_event({"message": {"data": "not base64"}})


def test_new_evidence_invalidates_approval_and_busy_input_is_rejected(environment):
    db, settings = environment
    headers = {"X-API-Key": "a-secret"}
    with TestClient(create_app(settings, db)) as client:
        submit(client)
        path = "/v1/incidents/inc-1"
        message = {"id": "m1", "content": "New deployment found"}
        assert client.post(path + "/messages", headers=headers, json=message).status_code == 409
        db.finish(
            db.pending()[0], {"status": "awaiting_approval", "proposed_actions": [{"id": "a1"}]}
        )
        version = db.get("acme", "inc-1")["proposal_version"]
        assert client.post(path + "/messages", headers=headers, json=message).status_code == 202
        assert db.get("acme", "inc-1")["proposal_version"] is None
        decision = {"id": "d1", "approved": True, "proposal_version": version, "action_ids": ["a1"]}
        assert (
            client.post(path + "/actions/decision", headers=headers, json=decision).status_code
            == 409
        )


def test_worker_failure_is_bounded_and_persists_no_secret(environment):
    db, settings = environment

    class BrokenFactory:
        @contextmanager
        def open(self, tenant):
            raise RuntimeError("secret provider response")
            yield

    with TestClient(create_app(settings, db)) as client:
        submit(client)
    event_id = db.pending()[0]["id"]
    worker = Worker(db, BrokenFactory(), max_attempts=2)
    with pytest.raises(RuntimeError):
        worker.process(event_id)
    assert worker.process(event_id) == "dead"
    assert worker.process(event_id) == "dead"
    assert db.get("acme", "inc-1")["status"] == "failed"
    assert "secret provider response" not in json.dumps(db.event(event_id), default=str)
