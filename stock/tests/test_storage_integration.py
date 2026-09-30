"""Opt-in adapter round trip against local INFRA; no test credentials are committed."""

import asyncio
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from stock_research.domain.models import MarketEvent, StockContext
from stock_research.storage.postgres import PostgresStore
from stock_research.storage.timescale import TimescaleBarStore


@pytest.mark.integration
def test_event_context_and_bar_round_trip() -> None:
    postgres_dsn = os.getenv("STOCK_TEST_DATABASE_URL")
    timescale_dsn = os.getenv("STOCK_TEST_TIMESCALE_URL")
    if not postgres_dsn or not timescale_dsn:
        pytest.skip("set STOCK_TEST_DATABASE_URL and STOCK_TEST_TIMESCALE_URL for integration")

    async def scenario() -> None:
        postgres = await PostgresStore.connect(postgres_dsn)
        timescale = await TimescaleBarStore.connect(timescale_dsn)
        try:
            await postgres.create_schema()
            await timescale.create_schema()
            now = datetime.now(timezone.utc)
            symbol = f"TEST{uuid4().hex[:12]}"
            event = MarketEvent(
                symbol=symbol, event_type="bar", occurred_at=now - timedelta(minutes=5),
                observed_at=now, source="test", source_id=f"bar:{symbol}",
                payload={"interval": "5min", "open": 1, "high": 2, "low": 1,
                         "close": 2, "volume": 10, "adjusted": False},
            )
            await postgres.append(event)
            await postgres.append(event)
            await timescale.append_bar(event)
            await timescale.append_bar(event)
            assert len(await postgres.history(symbol, now - timedelta(days=1), now)) == 1
            assert len(await timescale.bars(
                symbol, "5min", now - timedelta(days=1), now
            )) == 1
            context = StockContext(symbol=symbol, as_of=now, context_version=1)
            assert await postgres.compare_and_swap(context, 0)
            assert await postgres.compare_and_swap(
                context.model_copy(update={"context_version": 2}), 1
            )  # First valid update succeeds.
            assert not await postgres.compare_and_swap(
                context.model_copy(update={"context_version": 2}), 1
            )  # Stale update is rejected.
            assert await postgres.get(symbol) is not None
        finally:
            await timescale.close()
            await postgres.close()

    asyncio.run(scenario())
