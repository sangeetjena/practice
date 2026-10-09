"""Agent inputs/outputs and the durable CSV row contract."""

from typing import Literal
from uuid import UUID, uuid4

from pydantic import AwareDatetime, Field

from stock_research.models.market import Contract, StockSnapshot

Direction = Literal["UP", "DOWN", "FLAT", "INSUFFICIENT_EVIDENCE"]


class AgentNote(Contract):
    """Completion acknowledgement for ingestion/analysis synchronization tasks."""

    summary: str


class AnalysisPrediction(Contract):
    """One specialist's prediction based only on its bound evidence snapshot."""

    stock: str
    specialty: Literal["volume", "candlestick", "bollinger"]
    prediction: Direction
    reasoning: str


class AnalysisBundle(Contract):
    """Typed collection of the three independent specialist outputs."""

    predictions: list[AnalysisPrediction] = Field(default_factory=list)


class MasterPrediction(Contract):
    """Next completed trading-session direction and a concise evidence-based reason."""

    stock: str
    prediction: Direction
    reasoning: str
    confidence: float = Field(ge=0, le=1)
    horizon: Literal["next_completed_session"] = "next_completed_session"


class Outcome(Contract):
    """Code-calculated outcome: the LLM cannot change correctness or actual return."""

    prediction_id: UUID
    evaluated_at: AwareDatetime
    actual_price: float = Field(gt=0)
    actual_return: float
    verdict: Literal["CORRECT", "INCORRECT", "INCONCLUSIVE"]
    target_bar_time: AwareDatetime


class CritiqueResult(Contract):
    """Explains an objective outcome; separates original mistakes from later events."""

    prediction_id: UUID
    original_mistake: str | None = None
    later_invalidation: str | None = None
    suggestion: str


class LearningResult(Contract):
    """Historical lessons passed to the master; proposals do not alter tools or rules."""

    stock: str
    lessons: list[str] = Field(default_factory=list)
    summary: str


class ResearchRow(Contract):
    """One time-series CSV memory row. Review fields may be added after maturity."""

    prediction_id: UUID = Field(default_factory=uuid4)
    snapshot: StockSnapshot
    analytical: AnalysisBundle
    master: MasterPrediction
    learning: LearningResult
    outcome: Outcome | None = None
    critique: CritiqueResult | None = None


class RunRequest(Contract):
    """Run settings supplied by CLI or scheduler; as_of defaults to real current UTC."""

    watchlist: list[str] = Field(default_factory=list)
    market: Literal["US", "IN"] = "US"
    max_stocks: int = Field(default=3, ge=1, le=10)
    as_of: AwareDatetime


class RunState(Contract):
    """Master Flow state; durable memory resides in CSV rather than vector storage."""

    rows: list[ResearchRow] = Field(default_factory=list)


class MasterInput(Contract):
    """Master receives facts, specialist outputs, lessons and reference knowledge."""

    snapshot: StockSnapshot
    analytical: AnalysisBundle
    learner: LearningResult
    knowledge: str
    knowledge_status: str = "Reference guidance, not current market evidence"


class LearningInput(Contract):
    """Historical evaluated records and objectively calculated scoring statistics."""

    stock: str
    evaluated_count: int = Field(ge=0)
    accuracy: float | None = Field(default=None, ge=0, le=1)
    history: list[dict] = Field(default_factory=list)


class CritiqueInput(Contract):
    """Separates original facts from later outcome-window evidence for review."""

    original_prediction: MasterPrediction
    original_snapshot: StockSnapshot
    later_evidence: dict
    objective_outcome: Outcome
