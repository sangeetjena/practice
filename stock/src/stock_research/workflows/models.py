from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class WorkflowKind(StrEnum):
    LIVE_MONITOR = "live_monitor"
    DAILY_RESEARCH = "daily_research"
    MONTHLY_FUNDAMENTALS = "monthly_fundamentals"
    CRITIQUE = "critique"
    BACKTEST = "backtest"


class WorkflowStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class WorkflowRun(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    kind: WorkflowKind
    symbol: str | None = None
    status: WorkflowStatus = WorkflowStatus.QUEUED
    scheduled_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    idempotency_key: str
    trace_id: str | None = None
