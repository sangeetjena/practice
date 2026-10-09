"""Screener ports: India CSV exports and free Yahoo research data for the US.

Screener.in has no public API. No fabricated endpoint or session-cookie scraping.
"""

import asyncio
import csv
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from stock_research.models.market import Candidate


class ScreenerProvider(Protocol):
    async def discover(self, limit: int) -> list[Candidate]: ...


def number(value) -> float | None:
    try:
        result = float(str(value).replace(",", "").replace("%", ""))
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


class ScreenerIndiaCSV:
    """Explicit columns avoid silently mapping BSE codes to NSE trading symbols."""

    def __init__(self, path: str):
        self.path = Path(path)

    async def discover(self, limit: int) -> list[Candidate]:
        return await asyncio.to_thread(self._read, limit)

    def _read(self, limit: int) -> list[Candidate]:
        if not self.path.is_file():
            raise ValueError("configured Screener.in export does not exist")
        if self.path.stat().st_size > 5_000_000:
            raise ValueError("Screener export exceeds 5 MB")
        with self.path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if not {"symbol", "sector", "pe", "as_of"}.issubset(reader.fieldnames or []):
                raise ValueError(
                    "CSV requires symbol,sector,pe,as_of columns; see research runbook"
                )
            result = []
            for row in reader:
                symbol = row["symbol"].strip().upper()
                if not symbol.endswith((".NS", ".BO")):
                    raise ValueError("India symbols must include .NS or .BO exchange suffix")
                as_of = datetime.fromisoformat(row["as_of"].replace("Z", "+00:00"))
                now = datetime.now(UTC)
                if as_of.tzinfo is None or as_of > now or (now - as_of).days > 7:
                    raise ValueError(
                        "Screener export as_of must be timezone-aware and within 7 days"
                    )
                result.append(
                    Candidate(
                        symbol=symbol,
                        sector=row["sector"],
                        pe=number(row["pe"]),
                        debt_current=number(row.get("debt_current")),
                        debt_previous=number(row.get("debt_previous")),
                        revenue_growth=number(row.get("revenue_growth")),
                        order_growth=number(row.get("order_growth")),
                        evidence_id=uuid4(),
                        observed_at=now,
                        source="screener_in_export",
                        source_url=row.get("source_url") or "https://www.screener.in/",
                        dataset_as_of=as_of.isoformat(),
                    )
                )
        # Growth is an observed revenue proxy; it is not proof of future demand.
        return sorted(result, key=lambda c: c.revenue_growth or 0, reverse=True)[:limit]


class YahooScreener:
    async def discover(self, limit: int) -> list[Candidate]:
        return await asyncio.to_thread(self._fetch, limit)

    def _fetch(self, limit: int) -> list[Candidate]:
        import yfinance as yf

        sectors = [
            "Technology",
            "Industrials",
            "Healthcare",
            "Financial Services",
            "Consumer Cyclical",
            "Energy",
            "Basic Materials",
            "Communication Services",
            "Consumer Defensive",
            "Utilities",
            "Real Estate",
        ]
        quotes = []
        for sector in sectors:
            if len(quotes) >= limit:
                break
            query = yf.EquityQuery(
                "and",
                [yf.EquityQuery("eq", ["region", "us"]), yf.EquityQuery("eq", ["sector", sector])],
            )
            response = yf.screen(
                query, size=min(2, limit - len(quotes)), sortField="dayvolume", sortAsc=False
            )
            if not isinstance(response, dict) or "quotes" not in response:
                raise RuntimeError("Yahoo sector screener unavailable")
            quotes.extend(response["quotes"])
        if not quotes:
            raise RuntimeError("Yahoo screener returned no candidates")
        result = []
        for quote in quotes[:limit]:
            symbol = quote["symbol"]
            ticker = yf.Ticker(symbol)
            info = ticker.get_info()
            balance = ticker.get_balance_sheet()
            debt = []
            if balance is not None and "TotalDebt" in balance.index:
                debt = [
                    number(v)
                    for v in balance.sort_index(axis=1, ascending=False).loc["TotalDebt"].tolist()
                ]
            result.append(
                Candidate(
                    symbol=symbol,
                    sector=info.get("sector") or "Unknown",
                    pe=number(info.get("trailingPE")),
                    debt_current=debt[0] if debt else None,
                    debt_previous=debt[1] if len(debt) > 1 else None,
                    revenue_growth=number(info.get("revenueGrowth")),
                    order_growth=None,
                    evidence_id=uuid4(),
                    observed_at=datetime.now(UTC),
                    source="yahoo_finance",
                    source_url=f"https://finance.yahoo.com/quote/{symbol}/",
                )
            )
        return sorted(result, key=lambda c: c.revenue_growth or 0, reverse=True)
