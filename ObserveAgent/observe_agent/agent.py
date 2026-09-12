"""LangGraph incident workflow plus reviewed long-term knowledge updates."""

from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .actions import ActionExecutor, ActionPlanner
from .features import IncidentFeatureExtractor
from .knowledge import SQLiteKnowledgeStore
from .models import (
    ActionDecision,
    ActionRequest,
    ActionResult,
    ActionStatus,
    FeedbackDecision,
    Incident,
    IncidentFeatures,
    IncidentFeedback,
    SearchHit,
    TriageReport,
    WorkflowResponse,
    WorkflowStatus,
)
from .reasoner import Reasoner, RuleBasedReasoner


class IncidentState(TypedDict, total=False):
    incident: dict
    features: dict
    knowledge: list[dict]
    report: dict
    proposed_actions: list[dict]
    decision: dict
    action_results: list[dict]
    status: str


class ReflexionAgent:
    def __init__(
        self,
        features: IncidentFeatureExtractor,
        knowledge: SQLiteKnowledgeStore,
        reasoner: Reasoner | None = None,
        knowledge_limit: int = 5,
        action_planner: ActionPlanner | None = None,
        action_executor: ActionExecutor | None = None,
        checkpointer=None,
    ) -> None:
        self.features = features
        self.knowledge = knowledge
        self.reasoner = reasoner or RuleBasedReasoner()
        self.knowledge_limit = knowledge_limit
        self.action_planner = action_planner
        self.action_executor = action_executor
        self.graph = self._build_graph(checkpointer or InMemorySaver())

    def _build_graph(self, checkpointer):
        builder = StateGraph(IncidentState)
        builder.add_node("persist_incident", self._persist_incident)
        builder.add_node("extract_features", self._extract_features)
        builder.add_node("retrieve_knowledge", self._retrieve_knowledge)
        builder.add_node("diagnose", self._diagnose)
        builder.add_node("plan_actions", self._plan_actions)
        builder.add_node("approval_gate", self._approval_gate)
        builder.add_node("execute_actions", self._execute_actions)
        builder.add_node("reject_actions", self._reject_actions)
        builder.add_node("finalize", self._finalize)
        builder.add_edge(START, "persist_incident")
        builder.add_edge("persist_incident", "extract_features")
        builder.add_edge("extract_features", "retrieve_knowledge")
        builder.add_edge("retrieve_knowledge", "diagnose")
        builder.add_edge("diagnose", "plan_actions")
        builder.add_conditional_edges(
            "plan_actions", self._after_planning, {"approval": "approval_gate", "done": "finalize"}
        )
        builder.add_conditional_edges(
            "approval_gate",
            self._after_approval,
            {"execute": "execute_actions", "reject": "reject_actions"},
        )
        builder.add_node("reflect", self._reflect)
        builder.add_edge("execute_actions", "reflect")
        builder.add_edge("reflect", "finalize")
        builder.add_edge("reject_actions", "finalize")
        builder.add_edge("finalize", END)
        return builder.compile(checkpointer=checkpointer)

    def handle_incident(self, incident: Incident) -> WorkflowResponse:
        prior = self.knowledge.get_incident(incident.id)
        if prior is not None:
            if prior != incident:
                raise ValueError("incident ID already exists with a different payload")
            snapshot = self.graph.get_state(self._config(incident.id))
            if snapshot.values.get("report"):
                response = self._response(snapshot.values)
                if snapshot.next:
                    response.status = WorkflowStatus.AWAITING_APPROVAL
                return response
        result = self.graph.invoke(
            {"incident": incident.model_dump(mode="json")},
            config=self._config(incident.id),
        )
        return self._response(result)

    def decide_actions(self, incident_id: str, decision: ActionDecision) -> WorkflowResponse:
        if self.knowledge.get_incident(incident_id) is None:
            raise KeyError(f"incident {incident_id!r} was not found")
        snapshot = self.graph.get_state(self._config(incident_id))
        if not snapshot.next:
            raise ValueError("incident has no pending approval")
        known = {item["id"] for item in snapshot.values.get("proposed_actions", [])}
        if set(decision.action_ids) - known:
            raise ValueError("decision contains unknown action IDs")
        result = self.graph.invoke(
            Command(resume=decision.model_dump(mode="json")),
            config=self._config(incident_id),
        )
        return self._response(result)

    def _persist_incident(self, state: IncidentState) -> IncidentState:
        incident = Incident.model_validate(state["incident"])
        self.knowledge.save_incident(incident)
        return {"status": "investigating"}

    def _extract_features(self, state: IncidentState) -> IncidentState:
        incident = Incident.model_validate(state["incident"])
        features = self.features.extract(incident)
        self.knowledge.save_features(features)
        return {"features": features.model_dump(mode="json")}

    def _retrieve_knowledge(self, state: IncidentState) -> IncidentState:
        incident = Incident.model_validate(state["incident"])
        features = IncidentFeatures.model_validate(state["features"])
        hits = self.knowledge.search(
            self._retrieval_query(incident, features),
            tenant_id=incident.tenant_id,
            service=incident.service,
            limit=self.knowledge_limit,
        )
        return {"knowledge": [hit.model_dump(mode="json") for hit in hits]}

    def _diagnose(self, state: IncidentState) -> IncidentState:
        incident = Incident.model_validate(state["incident"])
        features = IncidentFeatures.model_validate(state["features"])
        hits = [SearchHit.model_validate(item) for item in state.get("knowledge", [])]
        report = self.reasoner.analyze(incident, features, hits)
        self.knowledge.save_report(report)
        return {"report": report.model_dump(mode="json")}

    def _plan_actions(self, state: IncidentState) -> IncidentState:
        if self.action_planner is None:
            return {"proposed_actions": []}
        incident = Incident.model_validate(state["incident"])
        report = TriageReport.model_validate(state["report"])
        actions = self.action_planner.plan(incident, report)
        for action in actions:
            self.knowledge.save_action_proposal(action)
        return {"proposed_actions": [action.model_dump(mode="json") for action in actions]}

    def _reflect(self, state: IncidentState) -> IncidentState:
        observations = [
            item
            for item in state.get("action_results", [])
            if item["status"] == "succeeded" and "body" in item.get("output", {})
        ]
        if not observations:
            return {}
        features = IncidentFeatures.model_validate(state["features"])
        for item in observations:
            features.context[f"untrusted_diagnostic:{item['action_id']}"] = item["output"]["body"]
        self.knowledge.save_features(features)
        revised = {**state, "features": features.model_dump(mode="json")}
        return {"features": revised["features"], **self._diagnose(revised)}

    @staticmethod
    def _after_planning(state: IncidentState) -> Literal["approval", "done"]:
        return "approval" if state.get("proposed_actions") else "done"

    @staticmethod
    def _approval_gate(state: IncidentState) -> IncidentState:
        decision = interrupt(
            {
                "question": "Approve these policy-checked incident actions?",
                "actions": state.get("proposed_actions", []),
            }
        )
        validated = ActionDecision.model_validate(decision)
        return {"decision": validated.model_dump(mode="json")}

    @staticmethod
    def _after_approval(state: IncidentState) -> Literal["execute", "reject"]:
        decision = ActionDecision.model_validate(state["decision"])
        return "execute" if decision.approved else "reject"

    def _execute_actions(self, state: IncidentState) -> IncidentState:
        if self.action_executor is None:
            raise RuntimeError("an action executor is required when actions are enabled")
        decision = ActionDecision.model_validate(state["decision"])
        selected = set(decision.action_ids)
        actions = [ActionRequest.model_validate(item) for item in state["proposed_actions"]]
        if selected:
            unknown = selected - {action.id for action in actions}
            if unknown:
                raise ValueError(f"unknown action IDs: {sorted(unknown)}")
            actions = [action for action in actions if action.id in selected]
        results = [self.action_executor.execute(action) for action in actions]
        return {"action_results": [result.model_dump(mode="json") for result in results]}

    def _reject_actions(self, state: IncidentState) -> IncidentState:
        decision = ActionDecision.model_validate(state["decision"])
        results: list[ActionResult] = []
        for item in state["proposed_actions"]:
            action = ActionRequest.model_validate(item)
            result = ActionResult(
                action_id=action.id,
                status=ActionStatus.REJECTED,
                message=f"Rejected by {decision.reviewer}; no external call was made.",
            )
            self.knowledge.save_action_result(result)
            results.append(result)
        return {"action_results": [result.model_dump(mode="json") for result in results]}

    @staticmethod
    def _finalize(state: IncidentState) -> IncidentState:
        return {"status": WorkflowStatus.COMPLETED.value}

    @staticmethod
    def _config(incident_id: str) -> dict:
        return {"configurable": {"thread_id": incident_id}}

    @staticmethod
    def _response(state: IncidentState) -> WorkflowResponse:
        report = TriageReport.model_validate(state["report"])
        return WorkflowResponse(
            incident_id=report.incident_id,
            status=(
                WorkflowStatus.AWAITING_APPROVAL
                if "__interrupt__" in state
                else WorkflowStatus.COMPLETED
            ),
            report=report,
            proposed_actions=[
                ActionRequest.model_validate(item) for item in state.get("proposed_actions", [])
            ],
            action_results=[
                ActionResult.model_validate(item) for item in state.get("action_results", [])
            ],
        )

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
            f"# Verification and reviewer notes\n"
            f"{feedback.notes or 'Resolution confirmed by reviewer.'}\n"
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
    def _retrieval_query(incident: Incident, features: IncidentFeatures) -> str:
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
