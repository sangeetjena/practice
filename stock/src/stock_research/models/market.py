"""Validated source data. Timestamps express when facts were observable."""

from datetime import date, timedelta
from typing import Any
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator


class Contract(BaseModel):
    """Common contract: reject unknown fields and non-finite numeric values."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Candidate(Contract):
    """One discovery candidate and the source snapshot supporting its selection."""

    symbol: str
    sector: str
    pe: float | None = None
    debt_current: float | None = None
    debt_previous: float | None = None
    revenue_growth: float | None = None
    order_growth: float | None = None
    evidence_id: UUID
    observed_at: AwareDatetime
    source: str
    source_url: str
    dataset_as_of: str | None = None


class DiscoveryResult(Contract):
    """Only symbols present in the bound screener/watchlist may be selected."""

    stocks: list[str] = Field(default_factory=list)
    reasoning: str

    @field_validator("stocks")
    @classmethod
    def safe_symbols(cls, values):
        if any(
            not v
            or len(v) > 24
            or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-^" for c in v)
            for v in values
        ):
            raise ValueError("Use valid uppercase exchange tickers")
        return list(dict.fromkeys(values))


class Bar(Contract):
    """Completed daily OHLCV bar; never use a partial current-session bar."""

    bar_time: AwareDatetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)

    @model_validator(mode="after")
    def valid_range(self):
        if self.high < max(self.open, self.close, self.low) or self.low > min(
            self.open, self.close
        ):
            raise ValueError("Invalid OHLC price range")
        return self


class TechnicalData(Contract):
    """Source prices and deterministic indicators returned by the technical tool."""

    stock: str
    observed_at: AwareDatetime
    source: str
    bars: list[Bar]
    current_price: float = Field(gt=0, description="Last completed daily close, not a live quote")
    indicators: dict[str, Any]


class FundamentalData(Contract):
    """Cached company snapshot; expiry is one calendar month from fetched_at."""

    stock: str
    fetched_at: AwareDatetime
    source: str
    indicators: dict[str, Any]


class EarningsData(Contract):
    """Known earnings dates for the current Monday-Sunday calendar week."""

    stock: str
    observed_at: AwareDatetime
    source: str
    dates: list[date] = Field(default_factory=list)
    status: str = "unknown"


class Article(Contract):
    """Sourced article. Its publication time must not exceed the run cutoff."""

    title: str
    published_at: AwareDatetime
    url: str = ""
    summary: str = ""


class NewsData(Contract):
    """Dated headlines plus the news agent's concise interpretation."""

    stock: str
    observed_at: AwareDatetime
    source: str
    articles: list[Article] = Field(default_factory=list)
    summary: str = ""


class StockSnapshot(Contract):
    """Immutable input shared by analytical/master agents for one stock/run."""

    date: AwareDatetime
    stock: str
    technical: TechnicalData
    fundamental: FundamentalData
    earnings: EarningsData
    news: NewsData

    @model_validator(mode="after")
    def consistent_source_scope(self):
        """Reject cross-stock, future-news or incomplete-bar input packets."""
        for item in [self.technical, self.fundamental, self.earnings, self.news]:
            if item.stock != self.stock:
                raise ValueError("Cross-stock source data")
        if any(
            t > self.date
            for t in [
                self.technical.observed_at,
                self.fundamental.fetched_at,
                self.earnings.observed_at,
                self.news.observed_at,
            ]
        ):
            raise ValueError("Source timestamp follows snapshot cutoff")
        bars = self.technical.bars
        if not bars or any(b.bar_time + timedelta(hours=24) > self.date for b in bars):
            raise ValueError("Snapshot needs completed daily bars")
        if any(a.bar_time >= b.bar_time for a, b in zip(bars, bars[1:])):
            raise ValueError("Bars must be strictly chronological")
        if self.technical.current_price != bars[-1].close:
            raise ValueError("Current price must equal the last completed close")
        if any(a.published_at > self.date for a in self.news.articles):
            raise ValueError("News follows snapshot cutoff")
        return self
