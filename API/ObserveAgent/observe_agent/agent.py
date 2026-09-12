"""Incident-triggered reflexion workflow and human-reviewed knowledge update."""

from __future__ import annotations

from .features import IncidentFeatureExtractor
from .knowledge import SQLiteKnowledgeStore
from .models import FeedbackDecision, Incident, IncidentFeedback, TriageReport
from .reasoner import Reasoner, RuleBasedReasoner


class ReflexionAgent:
    def __init__(
        self,
        features: IncidentFeatureExtractor,
        knowledge: SQLiteKnowledgeStore,
        reasoner: Reasoner | None = None,
        knowledge_limit: int = 5,
    ) -> None:
        self.features = features
        self.knowledge = knowledge
        self.reasoner = reasoner or RuleBasedReasoner()
        self.knowledge_limit = knowledge_limit

    def handle_incident(self, incident: Incident) -> TriageReport:
        self.knowledge.save_incident(incident)
        features = self.features.extract(incident)
        self.knowledge.save_features(features)
        query = self._retrieval_query(incident, features)
        hits = self.knowledge.search(
            query,
            tenant_id=incident.tenant_id,
            service=incident.service,
            limit=self.knowledge_limit,
        )
        report = self.reasoner.analyze(incident, features, hits)
        self.knowledge.save_report(report)
        return report

    def apply_feedback(self, incident_id: str, feedback: IncidentFeedback) -> list[str]:
        incident = self.knowledge.get_incident(incident_id)
        if incident is None:
            raise KeyError(f"incident {incident_id!r} was not found")
        self.knowledge.save_feedback(incident_id, feedback)
        if (
            feedback.decision not in {FeedbackDecision.ACCEPT, FeedbackDecision.EDIT}
            or not feedback.resolved
            or not feedback.confirmed_root_cause
            or not feedback.resolution
        ):
            return []

        source_id = f"incident-resolution:{incident.id}"
        document = (
            f"# Symptoms\n{incident.title}\n\n"
            f"# Confirmed root cause\n{feedback.confirmed_root_cause}\n\n"
            f"# Resolution\n{feedback.resolution}\n\n"
            f"# Verification and reviewer notes\n{feedback.notes or 'Resolution confirmed by reviewer.'}\n"
        )
        return self.knowledge.ingest(
            source_id,
            document,
            {
                "source_type": "incident_resolution",
                "review_status": "approved",
                "tenant_scope": incident.tenant_id,
                "service": incident.service,
                "environment": incident.environment,
                "incident_id": incident.id,
                "reviewer": feedback.reviewer,
                "root_cause": feedback.confirmed_root_cause,
            },
        )

    @staticmethod
    def _retrieval_query(incident: Incident, features) -> str:
        measured = " ".join(
            f"{name}={feature.current} delta={feature.delta}"
            for name, feature in features.values.items()
            if feature.current is not None
        )
        return " ".join(
            filter(
                None,
                [
                    incident.title,
                    incident.service,
                    incident.environment,
                    incident.route,
                    " ".join(incident.annotations.values()),
                    measured,
                ],
            )
        )
