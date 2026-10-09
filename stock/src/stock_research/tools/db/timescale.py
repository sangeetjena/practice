"""Append-only OHLCV storage on INFRA's TimescaleDB service."""

from datetime import datetime
from pathlib import Path
from typing import Any

import asyncpg

from stock_research.models.connectors import MarketEvent, require_aware


class TimescaleBarStore:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    @classmethod
    async def connect(cls, dsn: str) -> "TimescaleBarStore":
        if not dsn:
            raise ValueError("STOCK_TIMESCALE_URL is required")
        return cls(await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=5))

    async def close(self) -> None:
        await self.pool.close()

    async def create_schema(self) -> None:
        sql = (Path(__file__).parent / "sql" / "timescale.sql").read_text(encoding="utf-8")
        async with self.pool.acquire() as connection:
            await connection.execute(sql)

    async def append_bar(self, event: MarketEvent) -> None:
        if event.event_type != "bar":
            raise ValueError("TimescaleBarStore accepts bar events only")
        payload = event.payload
        async with self.pool.acquire() as connection:
            await connection.execute(
                """INSERT INTO market_bars
                   (symbol, interval, bar_time, observed_at, source, source_id,
                    open, high, low, close, volume, adjusted)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
                   ON CONFLICT (symbol, interval, bar_time, source, source_id) DO NOTHING""",
                event.symbol,
                str(payload["interval"]),
                event.occurred_at,
                event.observed_at,
                event.source,
                event.source_id,
                float(payload["open"]),
                float(payload["high"]),
                float(payload["low"]),
                float(payload["close"]),
                int(payload["volume"]),
                bool(payload["adjusted"]),
            )

    async def bars(
        self, symbol: str, interval: str, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        require_aware(start)
        require_aware(end)
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(
                """SELECT symbol, interval, bar_time, observed_at, source, source_id,
                          open, high, low, close, volume, adjusted
                   FROM market_bars WHERE symbol=$1 AND interval=$2
                     AND bar_time >= $3 AND bar_time < $4
                   ORDER BY bar_time, observed_at""",
                symbol,
                interval,
                start,
                end,
            )
        return [dict(row) for row in rows]
