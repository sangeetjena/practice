import asyncio
from datetime import UTC, datetime

import httpx
import pytest

from stock_research.tools.api.alpha_vantage import AlphaVantageProvider, ProviderError


def test_daily_history_normalizes_bar_and_preserves_observation_time() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        assert request.url.params["function"] == "TIME_SERIES_DAILY"
        assert request.url.params["symbol"] == "IBM"
        return httpx.Response(
            200,
            json={
                "Time Series (Daily)": {
                    "2026-09-29": {
                        "1. open": "100",
                        "2. high": "105",
                        "3. low": "98",
                        "4. close": "103",
                        "5. volume": "1000",
                    }
                }
            },
        )

    async def scenario() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            provider = AlphaVantageProvider("test-key", client=client)
            events = await provider.history(
                "IBM",
                datetime(2026, 9, 29, tzinfo=UTC),
                datetime(2026, 10, 1, tzinfo=UTC),
            )
            assert len(events) == 1
            assert events[0].event_type == "bar"
            assert events[0].occurred_at.isoformat() == "2026-09-29T04:00:00+00:00"
            assert events[0].observed_at > events[0].occurred_at
            assert events[0].payload["close"] == 103.0

    asyncio.run(scenario())


def test_provider_rejects_quota_message_without_echoing_secret() -> None:
    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda _: httpx.Response(200, json={"Note": "daily quota reached"})
            )
        ) as client:
            provider = AlphaVantageProvider("secret-key", client=client)
            with pytest.raises(ProviderError) as error:
                await provider.history(
                    "IBM",
                    datetime(2026, 9, 1, tzinfo=UTC),
                    datetime(2026, 10, 1, tzinfo=UTC),
                )
            assert "secret-key" not in str(error.value)

    asyncio.run(scenario())


def test_news_is_timestamped_at_ingestion_not_backdated() -> None:
    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda _: httpx.Response(
                    200,
                    json={
                        "feed": [
                            {
                                "url": "https://example.org/story",
                                "time_published": "20260929T120000",
                                "title": "Example",
                            }
                        ]
                    },
                )
            )
        ) as client:
            provider = AlphaVantageProvider("test-key", client=client)
            events = await provider.events({"IBM"}, datetime(2026, 9, 29, tzinfo=UTC))
            assert len(events) == 1
            assert events[0].occurred_at.isoformat() == "2026-09-29T12:00:00+00:00"
            assert events[0].observed_at > events[0].occurred_at

    asyncio.run(scenario())


def test_overview_refuses_historical_as_of() -> None:
    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"Symbol": "IBM"}))
        ) as client:
            provider = AlphaVantageProvider("test-key", client=client)
            with pytest.raises(ValueError, match="historical fundamental"):
                await provider.snapshot("IBM", datetime(2020, 1, 1, tzinfo=UTC))

    asyncio.run(scenario())
