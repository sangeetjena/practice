from datetime import datetime
from typing import Protocol
from uuid import UUID

from stock_research.domain.models import Critique, DecisionSnapshot, MarketEvent, StockContext


class EventStore(Protocol):
    async def append(self, event: MarketEvent) -> None: ...

    async def history(self, symbol: str, start: datetime, end: datetime) -> list[MarketEvent]: ...


class ContextStore(Protocol):
    async def get(self, symbol: str) -> StockContext | None: ...

    async def compare_and_swap(self, context: StockContext, expected_version: int) -> bool: ...


class DecisionStore(Protocol):
    async def save(self, decision: DecisionSnapshot) -> None: ...

    async def get(self, decision_id: UUID) -> DecisionSnapshot | None: ...

    async def save_critique(self, critique: Critique) -> None: ...
