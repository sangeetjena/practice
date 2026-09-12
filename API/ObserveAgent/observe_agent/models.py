"""Contracts shared by collection, retrieval, reasoning, and feedback."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class Severity(StrEnum):
    WARNING = "warning"
    CRITICAL = "critical"


class Incident(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    tenant_id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=500)
    service: str = Field(pattern=r"^[A-Za-z0-9_.:-]+$")
    environment: str = Field(default="production", pattern=r"^[A-Za-z0-9_.:-]+$")
    region: str = Field(default="unknown", pattern=r"^[A-Za-z0-9_.:-]+$")
    route: str | None = Field(default=None, max_length=300)
    severity: Severity = Severity.WARNING
    started_at: datetime = Field(default_factory=utc_now)
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)


class MetricFeature(BaseModel):
    name: str
    current: float | None
    baseline: float | None
    delta: float | None
    query: str
    source: str = "prometheus"


class IncidentFeatures(BaseModel):
    incident_id: str
    window_start: datetime
    window_end: datetime
    values: dict[str, MetricFeature]
    context: dict[str, str] = Field(default_factory=dict)
    missing_sources: list[str] = Field(default_factory=list)


class KnowledgeChunk(BaseModel):
    id: str
    source_id: str
    content: str
    metadata: dict[str, Any]
    embedding: list[float]
    version: int = 1
    created_at: datetime = Field(default_factory=utc_now)


class SearchHit(BaseModel):
    chunk_id: str
    source_id: str
    content: str
    metadata: dict[str, Any]
    score: float


class Hypothesis(BaseModel):
    cause: str
    confidence: float = Field(ge=0, le=1)
    supporting_evidence: list[str]
    contradicting_evidence: list[str] = Field(default_factory=list)
    verification_queries: list[str] = Field(default_factory=list)


class TriageReport(BaseModel):
    incident_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    summary: str
    known_facts: list[str]
    hypotheses: list[Hypothesis]
    recommended_actions: list[str]
    unknowns: list[str]
    citations: list[str]
    knowledge_hits: int


class FeedbackDecision(StrEnum):
    ACCEPT = "accept"
    EDIT = "edit"
    REJECT = "reject"


class IncidentFeedback(BaseModel):
    decision: FeedbackDecision
    reviewer: str = Field(min_length=1, max_length=200)
    confirmed_root_cause: str | None = Field(default=None, max_length=2_000)
    resolution: str | None = Field(default=None, max_length=5_000)
    notes: str | None = Field(default=None, max_length=5_000)
    resolved: bool = False
    attributes: dict[str, str] = Field(default_factory=dict)


class AlertmanagerAlert(BaseModel):
    status: str
    labels: dict[str, str]
    annotations: dict[str, str] = Field(default_factory=dict)
    startsAt: datetime


class AlertmanagerWebhook(BaseModel):
    status: str = "firing"
    alerts: list[AlertmanagerAlert]
