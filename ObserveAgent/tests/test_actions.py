from datetime import UTC, datetime

import pytest

from observe_agent.actions import ActionExecutor, ActionPlanner, ActionPolicy
from observe_agent.agent import ReflexionAgent
from observe_agent.config import Settings
from observe_agent.features import IncidentFeatureExtractor
from observe_agent.knowledge import SQLiteKnowledgeStore
from observe_agent.models import ActionDecision, ActionRequest, ActionType, Incident


class Metrics:
    def __init__(self):
        self.values = iter([100, 80, 0.08, 0.01, 0.9, 0.2])

    def instant_value(self, query, at):
        return next(self.values)


def settings(tmp_path, **changes):
    values = {
        "database_path": tmp_path / "actions.db",
        "action_allowlist": ("http_get",),
        "http_allowed_hosts": ("status.example.com",),
    }
    values.update(changes)
    return Settings(**values)


def incident():
    return Incident(
        id="inc-action",
        tenant_id="acme",
        title="Orders latency",
        service="orders",
        started_at=datetime(2026, 9, 12, 8, tzinfo=UTC),
        action_context={"diagnostic_url": "https://status.example.com/health"},
    )


def test_langgraph_interrupts_then_dry_runs_approved_action(tmp_path):
    configured = settings(tmp_path)
    store = SQLiteKnowledgeStore(configured.database_path)
    agent = ReflexionAgent(
        IncidentFeatureExtractor(Metrics()),
        store,
        action_planner=ActionPlanner(configured),
        action_executor=ActionExecutor(configured, store),
    )

    pending = agent.handle_incident(incident())
    completed = agent.decide_actions(
        incident().id,
        ActionDecision(approved=True, reviewer="sre@example.com"),
    )

    assert pending.status == "awaiting_approval"
    assert len(pending.proposed_actions) == 1
    assert completed.status == "completed"
    assert completed.action_results[0].status == "dry_run"


def test_rejected_action_makes_no_external_call(tmp_path):
    configured = settings(tmp_path)
    store = SQLiteKnowledgeStore(configured.database_path)
    agent = ReflexionAgent(
        IncidentFeatureExtractor(Metrics()),
        store,
        action_planner=ActionPlanner(configured),
        action_executor=ActionExecutor(configured, store),
    )
    agent.handle_incident(incident())

    completed = agent.decide_actions(
        incident().id,
        ActionDecision(approved=False, reviewer="sre@example.com"),
    )

    assert completed.action_results[0].status == "rejected"


def test_policy_rejects_non_allowlisted_and_private_targets(tmp_path):
    policy = ActionPolicy(settings(tmp_path))
    action = ActionRequest(
        id="a-1",
        incident_id="i-1",
        action_type=ActionType.HTTP_GET,
        description="fetch",
        parameters={"url": "https://evil.example.net/secrets"},
    )
    with pytest.raises(ValueError, match="not allowlisted"):
        policy.validate(action)

    private_policy = ActionPolicy(settings(tmp_path, http_allowed_hosts=("127.0.0.1",)))
    action.parameters["url"] = "https://127.0.0.1/admin"
    with pytest.raises(ValueError, match="private"):
        private_policy.validate(action)
