from typing import Protocol

from pydantic import BaseModel

from stock_research.domain.models import Critique, DecisionSnapshot, MarketEvent, StockContext


class AgentFinding(BaseModel):
    agent_name: str
    agent_version: str
    summary: str
    evidence_ids: list[str]
    confidence: float


class AnalysisAgent(Protocol):
    agent_name: str

    async def analyze(self, context: StockContext, events: list[MarketEvent]) -> AgentFinding: ...


class DecisionAgent(Protocol):
    async def decide(self, context: StockContext, findings: list[AgentFinding]) -> DecisionSnapshot: ...


class CritiqueAgent(Protocol):
    async def critique(
        self, decision: DecisionSnapshot, original_events: list[MarketEvent],
        subsequent_events: list[MarketEvent],
    ) -> Critique: ...


AGENT_ROLES = ("technical", "fundamental", "news", "sector", "macro", "risk", "decision", "critique")
