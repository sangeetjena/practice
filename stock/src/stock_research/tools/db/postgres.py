"""Durable event, context, decision, and critique records on INFRA's Citus coordinator."""

import json
from datetime import datetime
from pathlib import Path
from typing import overload
from uuid import UUID

import asyncpg

from stock_research.models.connectors import (
    Critique,
    DecisionSnapshot,
    MarketEvent,
    StockContext,
    require_aware,
)


class PostgresStore:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    @classmethod
    async def connect(cls, dsn: str) -> "PostgresStore":
        if not dsn:
            raise ValueError("STOCK_DATABASE_URL is required")
        return cls(await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=5))

    async def close(self) -> None:
        await self.pool.close()

    async def create_schema(self) -> None:
        sql = (Path(__file__).parent / "sql" / "postgres.sql").read_text(encoding="utf-8")
        async with self.pool.acquire() as connection:
            await connection.execute(sql)

    async def append(self, event: MarketEvent) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute(
                """INSERT INTO market_events
                   (event_id, symbol, event_type, occurred_at, observed_at, source, source_id, payload)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8::jsonb)
                   ON CONFLICT DO NOTHING""",
                event.event_id,
                event.symbol,
                event.event_type,
                event.occurred_at,
                event.observed_at,
                event.source,
                event.source_id,
                json.dumps(event.model_dump(mode="json")["payload"]),
            )

    async def history(self, symbol: str, start: datetime, end: datetime) -> list[MarketEvent]:
        require_aware(start)
        require_aware(end)
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(
                """SELECT event_id, symbol, event_type, occurred_at, observed_at, source,
                          source_id, payload FROM market_events
                   WHERE symbol=$1 AND occurred_at >= $2 AND occurred_at < $3
                   ORDER BY occurred_at, observed_at""",
                symbol,
                start,
                end,
            )
        return [
            MarketEvent.model_validate({**dict(row), "payload": json.loads(row["payload"])})
            for row in rows
        ]

    @overload
    async def get(self, identifier: str) -> StockContext | None: ...

    @overload
    async def get(self, identifier: UUID) -> DecisionSnapshot | None: ...

    async def get(self, identifier: str | UUID) -> StockContext | DecisionSnapshot | None:
        if isinstance(identifier, UUID):
            async with self.pool.acquire() as connection:
                row = await connection.fetchrow(
                    "SELECT snapshot FROM decisions WHERE decision_id=$1", identifier
                )
            return DecisionSnapshot.model_validate(json.loads(row["snapshot"])) if row else None
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                "SELECT context FROM stock_context WHERE symbol=$1", identifier
            )
        return StockContext.model_validate(json.loads(row["context"])) if row else None

    async def compare_and_swap(self, context: StockContext, expected_version: int) -> bool:
        if context.context_version != expected_version + 1:
            raise ValueError("new context version must be expected_version + 1")
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                """INSERT INTO stock_context (symbol, version, as_of, context)
                   VALUES ($1,$2,$3,$4::jsonb)
                   ON CONFLICT (symbol) DO UPDATE SET
                     version=EXCLUDED.version, as_of=EXCLUDED.as_of, context=EXCLUDED.context
                   WHERE stock_context.version=$5 RETURNING version""",
                context.symbol,
                context.context_version,
                context.as_of,
                context.model_dump_json(),
                expected_version,
            )
        return row is not None

    async def save(self, decision: DecisionSnapshot) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute(
                """INSERT INTO decisions
                   (decision_id, symbol, decided_at, cutoff_at, action, snapshot)
                   VALUES ($1,$2,$3,$4,$5,$6::jsonb)""",
                decision.decision_id,
                decision.symbol,
                decision.decided_at,
                decision.cutoff_at,
                decision.action.value,
                decision.model_dump_json(),
            )

    async def save_critique(self, critique: Critique) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute(
                """INSERT INTO critiques (critique_id, decision_id, evaluated_at, outcome, critique)
                   VALUES ($1,$2,$3,$4,$5::jsonb)""",
                critique.critique_id,
                critique.decision_id,
                critique.evaluated_at,
                critique.outcome.value,
                critique.model_dump_json(),
            )
