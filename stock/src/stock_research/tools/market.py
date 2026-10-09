"""Reusable online API adapters and deterministic extraction; no LLM calculations."""

import asyncio
import math
from datetime import UTC, datetime, timedelta
from statistics import mean, pstdev

from stock_research.models.market import (
    Article,
    Bar,
    EarningsData,
    FundamentalData,
    NewsData,
    TechnicalData,
)
from stock_research.tools.api.alpha_vantage import AlphaVantageProvider
from stock_research.tools.api.screener import ScreenerIndiaCSV, YahooScreener
from stock_research.tools.indicators import indicators


class MarketTools:
    def __init__(self, settings, memory):
        self.settings, self.memory = settings, memory

    async def discover(self, request):
        if request.watchlist:
            return request.watchlist[: request.max_stocks]
        if request.market == "IN" and not self.settings.screener_india_csv:
            raise ValueError("Configure STOCK_SCREENER_INDIA_CSV or supply an India watchlist")
        provider = (
            ScreenerIndiaCSV(self.settings.screener_india_csv)
            if request.market == "IN"
            else YahooScreener()
        )
        return [c.symbol for c in await provider.discover(request.max_stocks)]

    async def technical(self, stock, as_of):
        if self.settings.alpha_vantage_api_key and not stock.endswith((".NS", ".BO")):
            provider = AlphaVantageProvider(self.settings.alpha_vantage_api_key)
            try:
                events = await provider.history(stock, as_of - timedelta(days=90), as_of)
                bars = [
                    Bar(
                        bar_time=e.occurred_at,
                        **{k: e.payload[k] for k in ["open", "high", "low", "close", "volume"]},
                    )
                    for e in events
                ]
            finally:
                await provider.aclose()
            source = "alpha_vantage"
        else:
            bars = await asyncio.to_thread(self._bars, stock)
            source = "yahoo_finance"
        # Conservative daily completion avoids partial-session price leakage.
        bars = sorted(
            [b for b in bars if b.bar_time + timedelta(hours=24) <= as_of], key=lambda b: b.bar_time
        )
        if not bars:
            raise ValueError("No completed daily bars available")
        data = indicators([b.model_dump() for b in bars])
        if len(bars) >= 20:
            closes = [b.close for b in bars[-20:]]
            middle, deviation = mean(closes), pstdev(closes)
            last = bars[-1]
            data.update(
                bollinger_middle=middle,
                bollinger_upper=middle + 2 * deviation,
                bollinger_lower=middle - 2 * deviation,
                body=last.close - last.open,
                upper_wick=last.high - max(last.close, last.open),
                lower_wick=min(last.close, last.open) - last.low,
            )
        return TechnicalData(
            stock=stock,
            observed_at=as_of,
            source=source,
            bars=bars,
            current_price=bars[-1].close,
            indicators=data,
        )

    def _bars(self, stock):
        import yfinance as yf

        frame = yf.Ticker(stock).history(period="6mo", auto_adjust=False)
        return [
            Bar(
                bar_time=t.to_pydatetime().astimezone(UTC),
                open=float(r.Open),
                high=float(r.High),
                low=float(r.Low),
                close=float(r.Close),
                volume=float(r.Volume),
            )
            for t, r in frame.iterrows()
        ]

    async def fundamental(self, stock, as_of):
        cached = self.memory.cached_fundamentals(stock, as_of)
        if cached:
            return cached
        if self.settings.alpha_vantage_api_key and not stock.endswith((".NS", ".BO")):
            provider = AlphaVantageProvider(self.settings.alpha_vantage_api_key)
            try:
                value = (await provider.snapshot(stock, as_of))[0].payload
            finally:
                await provider.aclose()
            source = "alpha_vantage"
        else:
            value = await asyncio.to_thread(self._info, stock)
            source = "yahoo_finance"

        def number(*keys):
            for key in keys:
                try:
                    result = float(value[key])
                    if math.isfinite(result):
                        return result
                except (KeyError, ValueError, TypeError):
                    pass
            return None

        result = FundamentalData(
            stock=stock,
            fetched_at=as_of,
            source=source,
            indicators={
                "pe": number("PERatio", "trailingPE"),
                "market_cap": number("MarketCapitalization", "marketCap"),
                "eps": number("EPS", "trailingEps"),
                "debt_to_equity": number("debtToEquity"),
                "profit_margin": number("ProfitMargin", "profitMargins"),
                "revenue_growth": number("QuarterlyRevenueGrowthYOY", "revenueGrowth"),
            },
        )
        self.memory.save_fundamentals(result)
        return result

    def _info(self, stock):
        import yfinance as yf

        return yf.Ticker(stock).get_info()

    async def news(self, stock, as_of):
        import yfinance as yf

        items = await asyncio.to_thread(lambda: yf.Ticker(stock).get_news(count=15))
        articles = []
        for item in items:
            content = item.get("content", item)
            if not content.get("pubDate"):
                continue
            published = datetime.fromisoformat(content["pubDate"].replace("Z", "+00:00"))
            if published.tzinfo is None or not as_of - timedelta(days=7) <= published <= as_of:
                continue
            articles.append(
                Article(
                    title=content.get("title", ""),
                    published_at=published,
                    summary=content.get("summary", ""),
                    url=(content.get("canonicalUrl") or {}).get("url", ""),
                )
            )
        return NewsData(stock=stock, observed_at=as_of, source="yahoo_finance", articles=articles)

    async def earnings(self, stock, as_of):
        import yfinance as yf

        calendar = await asyncio.to_thread(lambda: yf.Ticker(stock).calendar)
        start = as_of.date() - timedelta(days=as_of.weekday())
        end = start + timedelta(days=6)
        values = calendar.get("Earnings Date", []) if isinstance(calendar, dict) else []
        dates = [v.date() if isinstance(v, datetime) else v for v in values]
        dates = [d for d in dates if start <= d <= end]
        return EarningsData(
            stock=stock,
            observed_at=as_of,
            source="yahoo_finance",
            dates=dates,
            status="scheduled" if dates else "not_reported_this_week",
        )
