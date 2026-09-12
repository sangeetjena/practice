from datetime import UTC, datetime

from observe_agent.agent import ReflexionAgent
from observe_agent.features import IncidentFeatureExtractor
from observe_agent.knowledge import SQLiteKnowledgeStore
from observe_agent.models import FeedbackDecision, Incident, IncidentFeedback


class SequenceMetrics:
    def __init__(self, values):
        self.values = iter(values)

    def instant_value(self, query, at):
        return next(self.values)


def build_incident(incident_id="inc-1", tenant="acme"):
    return Incident(
        id=incident_id,
        tenant_id=tenant,
        title="Orders latency after customer delay",
        service="orders",
        route="/api/v1/orders/{id}/customer",
        started_at=datetime(2026, 9, 12, 8, tzinfo=UTC),
    )


def test_incident_triage_and_human_resolution_improve_tenant_knowledge(tmp_path):
    store = SQLiteKnowledgeStore(tmp_path / "agent.db")
    store.ingest(
        "runbook:latency",
        "# Diagnostic\nInspect the slow dependency span.\n\n# Resolution\nRollback safely.",
        {
            "source_type": "runbook",
            "review_status": "approved",
            "tenant_scope": "global",
            "service": "orders",
        },
    )
    values = [100, 80, 0.08, 0.01, 0.9, 0.2]
    agent = ReflexionAgent(IncidentFeatureExtractor(SequenceMetrics(values)), store)

    workflow = agent.handle_incident(build_incident())
    report = workflow.report
    chunks = agent.apply_feedback(
        report.incident_id,
        IncidentFeedback(
            decision=FeedbackDecision.EDIT,
            reviewer="sre",
            confirmed_root_cause="Customer dependency delay exhausted the deadline.",
            resolution="Removed the delay and verified p95 recovery.",
            resolved=True,
        ),
    )

    assert report.hypotheses[0].confidence == 0.7
    assert store.get_features("inc-1").values["p95_latency_seconds"].current == 0.9
    assert report.citations
    assert chunks
    same_tenant = store.search("customer dependency delay", tenant_id="acme", service="orders")
    other_tenant = store.search("customer dependency delay", tenant_id="globex", service="orders")
    assert any(hit.source_id == "incident-resolution:inc-1" for hit in same_tenant)
    assert all(hit.source_id != "incident-resolution:inc-1" for hit in other_tenant)


def test_rejected_feedback_is_audited_but_not_indexed(tmp_path):
    store = SQLiteKnowledgeStore(tmp_path / "agent.db")
    agent = ReflexionAgent(IncidentFeatureExtractor(SequenceMetrics([1, 1, 0, 0, 0.1, 0.1])), store)
    agent.handle_incident(build_incident())

    chunks = agent.apply_feedback(
        "inc-1",
        IncidentFeedback(
            decision=FeedbackDecision.REJECT,
            reviewer="sre",
            confirmed_root_cause="Unverified guess",
            resolution="Restart everything",
            resolved=True,
        ),
    )

    assert chunks == []
    assert store.search("restart everything", tenant_id="acme", service="orders") == []
