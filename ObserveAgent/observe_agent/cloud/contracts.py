"""Public cloud contracts exclude caller-controlled tenant and reviewer identities.

Example: IncidentInput(id='inc-1', title='Slow orders', service='orders') is bound
to the tenant from authentication by the API, never by a request-body tenant_id.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..models import utc_now


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IncidentInput(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,100}$")
    title: str = Field(min_length=1, max_length=500)
    service: str = Field(pattern=r"^[A-Za-z0-9_.:-]{1,100}$")
    started_at: datetime = Field(default_factory=utc_now)
    environment: str = Field(default="production", pattern=r"^[A-Za-z0-9_-]{1,100}$")
    annotations: dict[str, str] = Field(default_factory=dict, max_length=20)
    action_context: dict[str, str] = Field(default_factory=dict, max_length=10)


class MessageInput(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,100}$")
    content: str = Field(min_length=1, max_length=8000)


class ApprovalInput(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,100}$")
    proposal_version: str = Field(min_length=1, max_length=100)
    approved: bool
    action_ids: list[str] = Field(min_length=1, max_length=10)


class FeedbackInput(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,100}$")
    decision: Literal["accept", "edit", "reject"]
    confirmed_root_cause: str | None = Field(default=None, max_length=2000)
    resolution: str | None = Field(default=None, max_length=5000)
    notes: str | None = Field(default=None, max_length=5000)
    resolved: bool = False
