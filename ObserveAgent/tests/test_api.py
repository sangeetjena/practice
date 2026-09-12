from datetime import UTC, datetime

from fastapi.testclient import TestClient

from observe_agent.agent import ReflexionAgent
from observe_agent.api import create_app
from observe_agent.features import IncidentFeatureExtractor
from observe_agent.knowledge import SQLiteKnowledgeStore


class ConstantMetrics:
    def instant_value(self, query, at):
        if "histogram_quantile" in query:
            return 0.9 if at.minute == 0 else 0.2
        if 'status=~"5.."' in query:
            return 0.08 if at.minute == 0 else 0.01
        return 100 if at.minute == 0 else 80


def test_create_read_report_and_apply_feedback(tmp_path):
    store = SQLiteKnowledgeStore(tmp_path / "api.db")
    agent = ReflexionAgent(IncidentFeatureExtractor(ConstantMetrics()), store)
    payload = {
        "id": "inc-api",
        "tenant_id": "acme",
        "title": "Orders latency",
        "service": "orders",
        "started_at": datetime(2026, 9, 12, 8, tzinfo=UTC).isoformat(),
    }

    with TestClient(create_app(agent)) as client:
        created = client.post("/v1/incidents", json=payload)
        fetched = client.get("/v1/incidents/inc-api/report")
        feedback = client.post(
            "/v1/incidents/inc-api/feedback",
            json={
                "decision": "accept",
                "reviewer": "sre",
                "confirmed_root_cause": "Slow customer dependency",
                "resolution": "Restored the prior configuration",
                "resolved": True,
            },
        )

    assert created.status_code == 200
    assert created.json()["status"] == "completed"
    assert fetched.json()["incident_id"] == "inc-api"
    assert feedback.json()["knowledge_updated"] is True


def test_alertmanager_webhook_triggers_only_firing_alerts(tmp_path):
    store = SQLiteKnowledgeStore(tmp_path / "api.db")
    agent = ReflexionAgent(IncidentFeatureExtractor(ConstantMetrics()), store)
    webhook = {
        "status": "firing",
        "alerts": [
            {
                "status": "firing",
                "labels": {"alertname": "HighLatency", "service": "orders"},
                "annotations": {"summary": "Orders are slow"},
                "startsAt": "2026-09-12T08:00:00Z",
            },
            {
                "status": "resolved",
                "labels": {"alertname": "Old", "service": "orders"},
                "startsAt": "2026-09-12T07:00:00Z",
            },
        ],
    }

    with TestClient(create_app(agent)) as client:
        response = client.post("/v1/alerts", json=webhook)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["report"]["summary"].endswith("Orders are slow")
