from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from stock_research.domain.models import require_aware


class TokenUsage(BaseModel):
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    cached_input_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)


class AIInvocation(BaseModel):
    event_id: UUID
    trace_id: str
    span_id: str
    decision_id: UUID | None = None
    workflow_run_id: UUID
    symbol: str | None = None
    agent_name: str
    agent_version: str
    prompt_version: str
    provider: str
    model: str
    model_version: str | None = None
    started_at: datetime
    ended_at: datetime
    latency_ms: int = Field(ge=0)
    usage: TokenUsage
    total_cost_usd: float | None = Field(default=None, ge=0)
    tool_calls: list[str] = Field(default_factory=list)
    status: str
    error_type: str | None = None

    _aware_start = field_validator("started_at")(require_aware)
    _aware_end = field_validator("ended_at")(require_aware)
