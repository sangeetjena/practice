"""Alpha Vantage HTTP adapter. All provider timestamps preserve first observation time."""

import asyncio
from collections.abc import AsyncIterator, Mapping
from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from stock_research.domain.models import MarketEvent, require_aware


class ProviderError(RuntimeError):
    """Upstream data is unavailable, malformed, or outside the account entitlement."""


class AlphaVantageProvider:
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(
        self,
        api_key: str,
        *,
        client: httpx.AsyncClient | None = None,
        exchange_timezone: str = "America/New_York",
        intraday_enabled: bool = False,
        full_history_enabled: bool = False,
        interval: str = "5min",
        poll_seconds: int = 300,
    ) -> None:
        if not api_key:
            raise ValueError("Alpha Vantage API key is required")
        if interval not in {"1min", "5min", "15min", "30min", "60min"}:
            raise ValueError("unsupported intraday interval")
        if poll_seconds < 1:
            raise ValueError("poll_seconds must be positive")
        self._api_key = api_key
        self._client = client or httpx.AsyncClient(timeout=20.0)
        self._owns_client = client is None
        self._timezone = ZoneInfo(exchange_timezone)
        self._intraday_enabled = intraday_enabled
        self._full_history_enabled = full_history_enabled
        self._interval = interval
        self._poll_seconds = poll_seconds

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def _query(self, function: str, **params: str) -> dict[str, Any]:
        data: Any = None
        for attempt in range(3):
            try:
                response = await self._client.get(
                    self.BASE_URL,
                    params={"function": function, "apikey": self._api_key, **params},
                )
                response.raise_for_status()
                data = response.json()
                break
            except (httpx.TransportError, httpx.HTTPStatusError, ValueError) as exc:
                status = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
                if attempt == 2 or (status is not None and status != 429 and status < 500):
                    # Never include the request URL: it contains the API key.
                    raise ProviderError(f"Alpha Vantage {function} request failed") from exc
                await asyncio.sleep(0.5 * (2**attempt))
        if not isinstance(data, dict):
            raise ProviderError(f"Alpha Vantage {function} returned a non-object response")
        for key in ("Error Message", "Note", "Information"):
            if key in data:
                raise ProviderError(f"Alpha Vantage {function}: {key} (check symbol, quota, or entitlement)")
        return data

    def _bar_events(
        self, symbol: str, data: Mapping[str, Any], *, interval: str, observed_at: datetime
    ) -> list[MarketEvent]:
        series_key = "Time Series (Daily)" if interval == "1d" else f"Time Series ({interval})"
        series = data.get(series_key)
        if not isinstance(series, dict):
            raise ProviderError(f"Alpha Vantage response is missing {series_key}")
        events: list[MarketEvent] = []
        for timestamp, values in series.items():
            if not isinstance(values, dict):
                raise ProviderError("bar payload is malformed")
            try:
                if interval == "1d":
                    local_time = datetime.combine(date.fromisoformat(timestamp), time.min, self._timezone)
                else:
                    local_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(
                        tzinfo=self._timezone
                    )
                occurred_at = local_time.astimezone(timezone.utc)
                payload = {
                    "interval": interval,
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": int(values["5. volume"]),
                    "adjusted": False,
                }
            except (KeyError, TypeError, ValueError) as exc:
                raise ProviderError("bar payload is malformed") from exc
            events.append(
                MarketEvent(
                    symbol=symbol,
                    event_type="bar",
                    occurred_at=occurred_at,
                    observed_at=observed_at,
                    source="alpha_vantage",
                    source_id=f"bar:{symbol}:{interval}:{timestamp}",
                    payload=payload,
                )
            )
        return sorted(events, key=lambda event: event.occurred_at)

    async def history(self, symbol: str, start: datetime, end: datetime) -> list[MarketEvent]:
        require_aware(start)
        require_aware(end)
        if end <= start:
            raise ValueError("end must follow start")
        data = await self._query(
            "TIME_SERIES_DAILY", symbol=symbol,
            outputsize="full" if self._full_history_enabled else "compact",
        )
        observed_at = datetime.now(timezone.utc)
        events = self._bar_events(symbol, data, interval="1d", observed_at=observed_at)
        if events and not self._full_history_enabled and start < events[0].occurred_at - timedelta(days=7):
            raise ProviderError("requested history predates the compact window; enable full history entitlement")
        return [event for event in events if start <= event.occurred_at < end]

    async def snapshot(self, symbol: str, as_of: datetime) -> list[MarketEvent]:
        require_aware(as_of)
        # Current OVERVIEW cannot reconstruct a historical point-in-time fundamental snapshot.
        if as_of < datetime.now(timezone.utc) - timedelta(minutes=1):
            raise ValueError("historical fundamental snapshots require a historical data provider")
        data = await self._query("OVERVIEW", symbol=symbol)
        observed_at = datetime.now(timezone.utc)
        if not data or not data.get("Symbol"):
            raise ProviderError("Alpha Vantage OVERVIEW returned no company data")
        return [
            MarketEvent(
                symbol=symbol,
                event_type="fundamental_overview",
                occurred_at=observed_at,
                observed_at=observed_at,
                source="alpha_vantage",
                source_id=f"overview:{symbol}:{observed_at.isoformat()}",
                payload=data,
            )
        ]

    async def events(self, symbols: set[str], since: datetime) -> list[MarketEvent]:
        require_aware(since)
        if not symbols:
            return []
        result: list[MarketEvent] = []
        # One ticker per request avoids the API's multi-ticker intersection semantics.
        for symbol in sorted(symbols):
            data = await self._query(
                "NEWS_SENTIMENT", tickers=symbol,
                time_from=since.astimezone(timezone.utc).strftime("%Y%m%dT%H%M"), limit="1000",
            )
            feed = data.get("feed")
            if not isinstance(feed, list):
                raise ProviderError("Alpha Vantage NEWS_SENTIMENT response is missing feed")
            observed_at = datetime.now(timezone.utc)
            for article in feed:
                if not isinstance(article, dict):
                    raise ProviderError("news article payload is malformed")
                try:
                    published = datetime.strptime(
                        article["time_published"], "%Y%m%dT%H%M%S"
                    ).replace(tzinfo=timezone.utc)
                except (KeyError, TypeError, ValueError) as exc:
                    raise ProviderError("news publication time is malformed") from exc
                if published < since:
                    continue
                article_id = str(article.get("url") or sha256(repr(article).encode()).hexdigest())
                result.append(
                    MarketEvent(
                        symbol=symbol,
                        event_type="news",
                        occurred_at=published,
                        observed_at=observed_at,
                        source="alpha_vantage",
                        source_id=f"news:{symbol}:{article_id}",
                        payload=article,
                    )
                )
        return result

    async def stream(self, symbols: set[str]) -> AsyncIterator[MarketEvent]:
        if not self._intraday_enabled:
            raise ProviderError("intraday polling requires an enabled premium market-data entitlement")
        seen: set[str] = set()
        while True:
            current: set[str] = set()
            for symbol in sorted(symbols):
                for event in await self.intraday_recent(symbol):
                    current.add(event.source_id)
                    if event.source_id not in seen:
                        seen.add(event.source_id)
                        yield event
            seen = current
            await asyncio.sleep(self._poll_seconds)

    async def intraday_recent(self, symbol: str) -> list[MarketEvent]:
        if not self._intraday_enabled:
            raise ProviderError("intraday polling requires an enabled premium market-data entitlement")
        data = await self._query(
            "TIME_SERIES_INTRADAY", symbol=symbol, interval=self._interval,
            outputsize="compact", adjusted="false",
        )
        observed_at = datetime.now(timezone.utc)
        bar_minutes = int(self._interval.removesuffix("min"))
        return [
            event for event in self._bar_events(
                symbol, data, interval=self._interval, observed_at=observed_at
            ) if event.occurred_at + timedelta(minutes=bar_minutes) <= observed_at
        ]
