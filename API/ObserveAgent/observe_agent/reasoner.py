"""Explainable baseline reasoner; replaceable by a tool-calling model adapter."""

from __future__ import annotations

from typing import Protocol

from .models import Hypothesis, Incident, IncidentFeatures, SearchHit, TriageReport


class Reasoner(Protocol):
    def analyze(
        self,
        incident: Incident,
        features: IncidentFeatures,
        knowledge: list[SearchHit],
    ) -> TriageReport: ...


class RuleBasedReasoner:
    """Deterministic reasoner that makes the lab runnable without an LLM account."""

    def analyze(
        self,
        incident: Incident,
        features: IncidentFeatures,
        knowledge: list[SearchHit],
    ) -> TriageReport:
        facts: list[str] = []
        hypotheses: list[Hypothesis] = []
        actions: list[str] = []
        unknowns = list(features.missing_sources)

        for feature in features.values.values():
            if feature.current is not None:
                baseline = "unknown" if feature.baseline is None else f"{feature.baseline:.4g}"
                facts.append(f"{feature.name} is {feature.current:.4g}; baseline is {baseline}.")

        latency = features.values["p95_latency_seconds"]
        errors = features.values["error_rate_ratio"]
        if latency.current is not None and latency.current > 0.5:
            confidence = 0.70 if latency.delta is not None and latency.delta > 0.2 else 0.55
            hypotheses.append(
                Hypothesis(
                    cause="A latency regression exists in the service or one of its dependencies.",
                    confidence=confidence,
                    supporting_evidence=[
                        f"p95 latency is {latency.current:.3f}s",
                        f"change from baseline is {latency.delta:.3f}s"
                        if latency.delta is not None
                        else "baseline is missing",
                    ],
                    verification_queries=[
                        "Open representative traces and compare child-span duration by service.",
                        "Compare latency by deployed version and recent configuration change.",
                    ],
                )
            )
        if errors.current is not None and errors.current > 0.05:
            hypotheses.append(
                Hypothesis(
                    cause="A server or downstream failure is increasing 5xx responses.",
                    confidence=0.65,
                    supporting_evidence=[f"5xx ratio is {errors.current:.2%}"],
                    verification_queries=[
                        "Group 5xx responses by route and status.",
                        "Inspect correlated traces and new error-log templates.",
                    ],
                )
            )
        if not hypotheses:
            hypotheses.append(
                Hypothesis(
                    cause="The supplied metric features do not yet isolate a root cause.",
                    confidence=0.25,
                    supporting_evidence=["No configured threshold is clearly breached."],
                    verification_queries=["Inspect alert labels and telemetry coverage."],
                )
            )

        citations: list[str] = []
        for hit in knowledge[:3]:
            citations.append(f"{hit.source_id}#{hit.chunk_id}")
            section = hit.metadata.get("section", "retrieved guidance")
            actions.append(f"Review {section} from {hit.source_id} before changing production.")
        actions.extend(
            [
                "Run the verification queries with read-only credentials.",
                "Ask the service owner to approve any state-changing remediation.",
                "Verify the original SLO after the action and roll back if it does not recover.",
            ]
        )
        if not knowledge:
            unknowns.append("No approved matching knowledge was retrieved.")
        return TriageReport(
            incident_id=incident.id,
            summary=f"Triage for {incident.service}: {incident.title}",
            known_facts=facts,
            hypotheses=sorted(hypotheses, key=lambda item: item.confidence, reverse=True)[:3],
            recommended_actions=actions,
            unknowns=unknowns,
            citations=citations,
            knowledge_hits=len(knowledge),
        )
