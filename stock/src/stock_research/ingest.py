"""Run real provider pulls and persist normalized events to INFRA databases."""

import argparse
import asyncio
from datetime import datetime, timedelta, timezone

from stock_research.config import get_settings
from stock_research.domain.models import MarketEvent
from stock_research.providers.alpha_vantage import AlphaVantageProvider
from stock_research.storage.postgres import PostgresStore
from stock_research.storage.timescale import TimescaleBarStore


def _required(value: str | None, name: str) -> str:
    if not value:
        raise ValueError(f"{name} must be configured in stock/.env")
    return value


async def run(command: str, symbol: str | None, since: datetime | None) -> int:
    settings = get_settings()
    postgres = await PostgresStore.connect(_required(settings.database_url, "STOCK_DATABASE_URL"))
    timescale: TimescaleBarStore | None = None
    try:
        if command == "init-db":
            timescale = await TimescaleBarStore.connect(
                _required(settings.timescale_url, "STOCK_TIMESCALE_URL")
            )
            await postgres.create_schema()
            await timescale.create_schema()
            return 0

        if symbol is None:
            raise ValueError("--symbol is required for ingest")
        provider = AlphaVantageProvider(
            _required(settings.alpha_vantage_api_key, "STOCK_ALPHA_VANTAGE_API_KEY"),
            exchange_timezone=settings.alpha_vantage_exchange_timezone,
            intraday_enabled=settings.alpha_vantage_intraday_enabled,
            full_history_enabled=settings.alpha_vantage_full_history_enabled,
            interval=settings.alpha_vantage_interval,
            poll_seconds=settings.alpha_vantage_poll_seconds,
        )
        try:
            now = datetime.now(timezone.utc)
            events: list[MarketEvent]
            if command == "daily":
                events = await provider.history(symbol, since or now - timedelta(days=90), now)
            elif command == "fundamentals":
                events = await provider.snapshot(symbol, now)
            elif command == "news":
                events = await provider.events({symbol}, since or now - timedelta(days=1))
            elif command == "intraday":
                events = await provider.intraday_recent(symbol)
            else:
                raise ValueError(f"unsupported command: {command}")
            if any(event.event_type == "bar" for event in events):
                timescale = await TimescaleBarStore.connect(
                    _required(settings.timescale_url, "STOCK_TIMESCALE_URL")
                )
            for event in events:
                await postgres.append(event)
                if event.event_type == "bar" and timescale is not None:
                    await timescale.append_bar(event)
            return len(events)
        finally:
            await provider.aclose()
    finally:
        if timescale is not None:
            await timescale.close()
        await postgres.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull stock data and persist it to INFRA")
    parser.add_argument("command", choices=("init-db", "daily", "fundamentals", "news", "intraday"))
    parser.add_argument("--symbol")
    parser.add_argument("--since", help="UTC ISO-8601 timestamp for daily or news pulls")
    args = parser.parse_args()
    since = datetime.fromisoformat(args.since.replace("Z", "+00:00")) if args.since else None
    if since is not None and (since.tzinfo is None or since.utcoffset() is None):
        parser.error("--since requires a timezone")
    count = asyncio.run(run(args.command, args.symbol, since))
    print(f"Stored {count} events")


if __name__ == "__main__":
    main()
