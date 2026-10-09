"""Explicit synthetic fixtures for orchestration testing without APIs or LLMs."""

from datetime import timedelta
from statistics import mean, pstdev

from stock_research.models.market import Bar, EarningsData, FundamentalData, NewsData, TechnicalData
from stock_research.tools.indicators import indicators
from stock_research.tools.market import MarketTools


class OfflineMarketTools(MarketTools):
    async def discover(self, request):
        return (request.watchlist or ["IBM"])[: request.max_stocks]

    async def technical(self, stock, as_of):
        origin = as_of.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=70)
        bars = []
        for i in range(69):
            timestamp = origin + timedelta(days=i)
            if timestamp.weekday() < 5:
                close = 100 + timestamp.toordinal() % 100 * 0.1
                bars.append(
                    Bar(
                        bar_time=timestamp,
                        open=close - 0.2,
                        high=close + 0.5,
                        low=close - 0.5,
                        close=close,
                        volume=1000 + i,
                    )
                )
        data = indicators([b.model_dump() for b in bars])
        closes = [b.close for b in bars[-20:]]
        middle = mean(closes)
        sd = pstdev(closes)
        data.update(
            bollinger_middle=middle,
            bollinger_upper=middle + 2 * sd,
            bollinger_lower=middle - 2 * sd,
        )
        return TechnicalData(
            stock=stock,
            observed_at=as_of,
            source="SYNTHETIC",
            bars=bars,
            current_price=bars[-1].close,
            indicators=data,
        )

    async def fundamental(self, stock, as_of):
        cached = self.memory.cached_fundamentals(stock, as_of)
        if cached:
            return cached
        value = FundamentalData(
            stock=stock, fetched_at=as_of, source="SYNTHETIC", indicators={"pe": 15, "eps": 5}
        )
        self.memory.save_fundamentals(value)
        return value

    async def earnings(self, stock, as_of):
        return EarningsData(stock=stock, observed_at=as_of, source="SYNTHETIC")

    async def news(self, stock, as_of):
        return NewsData(
            stock=stock,
            observed_at=as_of,
            source="SYNTHETIC",
            summary="Synthetic fixture, not actual news.",
        )
