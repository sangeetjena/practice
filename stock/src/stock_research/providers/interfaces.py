from collections.abc import AsyncIterator
from datetime import datetime
from typing import Protocol

from stock_research.domain.models import MarketEvent


class MarketDataProvider(Protocol):
    def stream(self, symbols: set[str]) -> AsyncIterator[MarketEvent]: ...

    async def history(self, symbol: str, start: datetime, end: datetime) -> list[MarketEvent]: ...


class FundamentalProvider(Protocol):
    async def snapshot(self, symbol: str, as_of: datetime) -> list[MarketEvent]: ...


class NewsProvider(Protocol):
    async def events(self, symbols: set[str], since: datetime) -> list[MarketEvent]: ...
