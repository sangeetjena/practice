"""Read historical point-in-time bars and fundamentals from existing INFRA databases."""

from __future__ import annotations

import asyncpg
import os
from datetime import datetime, timezone


async def load_history(timescale_url: str, postgres_url: str, symbol: str) -> tuple[list[dict], list[dict]]:
    # The local kind databases use plain Postgres connections. Explicit modes
    # override libpq/PGSSLMODE defaults that can attempt an SSL handshake and
    # cause kubectl port-forward to close on a connection reset.
    timescale = await asyncpg.connect(
        timescale_url, ssl=os.getenv("ML_TIMESCALE_SSLMODE", "disable")
    )
    postgres = None
    try:
        postgres = await asyncpg.connect(
            postgres_url, ssl=os.getenv("ML_DATABASE_SSLMODE", "disable")
        )
        rows = await timescale.fetch(
            """SELECT bar_time, observed_at, close, volume, source FROM market_bars
               WHERE symbol=$1 AND interval='1d' AND adjusted=false
               ORDER BY bar_time, observed_at""", symbol.upper()
        )
        # Deterministic first-observed source per bar; exclude revisions arriving later.
        bars_by_time: dict[datetime, dict] = {}
        for row in rows:
            bar = dict(row)
            bars_by_time.setdefault(bar["bar_time"], bar)
        fundamentals = await postgres.fetch(
            """SELECT observed_at, payload FROM market_events
               WHERE symbol=$1 AND event_type='fundamental_overview'
               ORDER BY observed_at""", symbol.upper()
        )
        return list(bars_by_time.values()), [dict(row) for row in fundamentals]
    finally:
        await timescale.close()
        if postgres is not None:
            await postgres.close()


def pe_as_of(events: list[dict], cutoff: datetime) -> float | None:
    value = None
    for event in events:
        if event["observed_at"] > cutoff:
            break
        raw = event["payload"]
        if isinstance(raw, str):
            import json
            raw = json.loads(raw)
        candidate = raw.get("PERatio")
        try:
            number = float(candidate)
            if 0 < number < 1000:
                value = number
        except (TypeError, ValueError):
            pass
    return value
