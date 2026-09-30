from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from stock_research.domain.models import DecisionAction, DecisionSnapshot, EvidenceRef
from stock_research.rules.engine import Condition, Operator, Rule, evaluate


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_rule_requires_every_metric() -> None:
    rule = Rule(rule_id="breakout", version="1", conditions=[
        Condition(metric="volume_ratio", operator=Operator.GT, threshold=2),
        Condition(metric="rsi", operator=Operator.GT, threshold=60),
    ])
    assert not evaluate(rule, {"volume_ratio": 3}, NOW).triggered
    assert evaluate(rule, {"volume_ratio": 3, "rsi": 61}, NOW).triggered


def test_decision_rejects_future_evidence() -> None:
    from datetime import timedelta

    with pytest.raises(ValidationError):
        DecisionSnapshot(
            symbol="ABC", decided_at=NOW, cutoff_at=NOW, action=DecisionAction.WATCH,
            confidence=0.5, horizon_seconds=86400, rationale="test",
            evidence=[EvidenceRef(event_id=uuid4(), observed_at=NOW + timedelta(seconds=1), source="feed")],
            rule_version="1", prompt_version="1", agent_version="1", context_version=1,
            input_snapshot_hash="sha256:test",
        )
