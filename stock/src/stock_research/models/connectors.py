"""Point-in-time contracts shared across feeds, rules, agents, and review."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


def require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must include a timezone")
    return value


class DecisionAction(StrEnum):
    ENTER = "ENTER"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    EXIT = "EXIT"
    WATCH = "WATCH"


class ThesisStatus(StrEnum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    CHALLENGED = "challenged"
    INVALIDATED = "invalidated"
    CLOSED = "closed"


class MarketEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    symbol: str
    event_type: str
    occurred_at: datetime
    observed_at: datetime
    source: str
    source_id: str
    payload: dict[str, Any] = Field(default_factory=dict)

    _aware_occurred = field_validator("occurred_at")(require_aware)
    _aware_observed = field_validator("observed_at")(require_aware)


class EvidenceRef(BaseModel):
    event_id: UUID
    observed_at: datetime
    source: str

    _aware_observed = field_validator("observed_at")(require_aware)


class Thesis(BaseModel):
    thesis_id: UUID = Field(default_factory=uuid4)
    symbol: str
    status: ThesisStatus = ThesisStatus.PROPOSED
    narrative: str
    created_at: datetime
    updated_at: datetime
    invalidation_conditions: list[str] = Field(default_factory=list)
    watch_conditions: list[str] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)

    _aware_created = field_validator("created_at")(require_aware)
    _aware_updated = field_validator("updated_at")(require_aware)


class StockContext(BaseModel):
    symbol: str
    as_of: datetime
    active_thesis: Thesis | None = None
    latest_decision_id: UUID | None = None
    open_paper_position_id: UUID | None = None
    active_risks: list[str] = Field(default_factory=list)
    approved_lessons: list[str] = Field(default_factory=list)
    watch_conditions: list[str] = Field(default_factory=list)
    context_version: int = Field(ge=1, default=1)

    _aware_as_of = field_validator("as_of")(require_aware)


class DecisionSnapshot(BaseModel):
    decision_id: UUID = Field(default_factory=uuid4)
    symbol: str
    decided_at: datetime
    cutoff_at: datetime
    action: DecisionAction
    confidence: float = Field(ge=0, le=1)
    horizon_seconds: int = Field(gt=0)
    rationale: str
    evidence: list[EvidenceRef]
    rule_version: str
    prompt_version: str
    agent_version: str
    context_version: int = Field(ge=1)
    input_snapshot_hash: str
    target_price: float | None = Field(default=None, gt=0)
    stop_price: float | None = Field(default=None, gt=0)

    _aware_decided = field_validator("decided_at")(require_aware)
    _aware_cutoff = field_validator("cutoff_at")(require_aware)

    @model_validator(mode="after")
    def check_point_in_time(self) -> "DecisionSnapshot":
        if self.cutoff_at > self.decided_at:
            raise ValueError("cutoff cannot follow the decision")
        if any(item.observed_at > self.cutoff_at for item in self.evidence):
            raise ValueError("decision evidence was not available at cutoff")
        return self


class CritiqueOutcome(StrEnum):
    SUPPORTED = "supported"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


class Critique(BaseModel):
    critique_id: UUID = Field(default_factory=uuid4)
    decision_id: UUID
    evaluated_at: datetime
    outcome: CritiqueOutcome
    original_reasoning_issue: str | None = None
    later_invalidation: str | None = None
    evidence_available_at_decision: list[EvidenceRef] = Field(default_factory=list)
    subsequent_event_ids: list[UUID] = Field(default_factory=list)
    proposed_improvement_id: UUID | None = None

    _aware_evaluated = field_validator("evaluated_at")(require_aware)
