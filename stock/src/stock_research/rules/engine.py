"""Small auditable rule evaluator; rule definitions are reviewed code/config."""
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from stock_research.domain.models import require_aware


class Operator(StrEnum):
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"


class Condition(BaseModel):
    metric: str
    operator: Operator
    threshold: float


class Rule(BaseModel):
    rule_id: str
    version: str
    conditions: list[Condition] = Field(min_length=1)
    cooldown_seconds: int = Field(ge=0, default=0)


class RuleResult(BaseModel):
    rule_id: str
    rule_version: str
    triggered: bool
    evaluated_at: datetime
    missing_metrics: list[str]


def evaluate(rule: Rule, metrics: dict[str, float], evaluated_at: datetime) -> RuleResult:
    require_aware(evaluated_at)
    missing = [condition.metric for condition in rule.conditions if condition.metric not in metrics]
    checks = {
        Operator.GT: lambda value, limit: value > limit,
        Operator.GTE: lambda value, limit: value >= limit,
        Operator.LT: lambda value, limit: value < limit,
        Operator.LTE: lambda value, limit: value <= limit,
    }
    triggered = not missing and all(
        checks[condition.operator](metrics[condition.metric], condition.threshold)
        for condition in rule.conditions
    )
    return RuleResult(
        rule_id=rule.rule_id,
        rule_version=rule.version,
        triggered=triggered,
        evaluated_at=evaluated_at,
        missing_metrics=missing,
    )
