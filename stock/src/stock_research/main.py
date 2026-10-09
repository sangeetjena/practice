"""CrewAI Flow entrypoint; run via crewai run or python -m stock_research.main."""

import argparse
import asyncio
import csv
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from stock_research.config import Settings
from stock_research.models.market import DiscoveryResult
from stock_research.models.prediction import RunRequest
from stock_research.tools.csv_memory import CsvMemory
from stock_research.tools.market import MarketTools
from stock_research.tools.offline import OfflineMarketTools


async def execute(request, settings):
    # Framework imports initialize runtime paths; use a project-local directory.
    os.environ["CREWAI_STORAGE_DIR"] = str((Path(settings.data_dir) / ".crewai-runtime").resolve())
    from stock_research.flow.executor import CrewExecutor
    from stock_research.flow.master import StockResearchFlow

    if not settings.offline and abs((datetime.now(UTC) - request.as_of).total_seconds()) > 300:
        raise ValueError(
            "Historical replay requires historical source snapshots; use offline tests for --as-of"
        )
    directory = Path(settings.data_dir) / "offline" if settings.offline else Path(settings.data_dir)
    memory = CsvMemory(directory)
    market = (OfflineMarketTools if settings.offline else MarketTools)(settings, memory)
    # One master run at a time avoids duplicate reviews and conflicting output files.
    from filelock import FileLock

    with FileLock(str(directory / "workflow.lock"), timeout=0):
        executor = CrewExecutor(settings, market, memory)
        try:
            return await StockResearchFlow(request, executor).kickoff_async()
        except Exception as exc:
            executor.log("Run failed", {"error_code": type(exc).__name__})
            raise


def kickoff():
    load_dotenv(override=False)
    os.environ.setdefault("OTEL_SDK_DISABLED", "true")
    if sys.platform == "win32":
        for stream in [sys.stdout, sys.stderr]:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="CSV-memory CrewAI stock prediction Flow")
    parser.add_argument(
        "--stocks", nargs="*", help="Exchange tickers; otherwise read watchlist or discover"
    )
    parser.add_argument("--market", choices=["US", "IN"], default="US")
    parser.add_argument("--max-stocks", type=int, default=3)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Synthetic providers/agent stand-ins; isolated CSV directory",
    )
    parser.add_argument("--as-of", help="Timezone-aware ISO timestamp; offline replay only")
    parser.add_argument("--data-dir")
    parser.add_argument("--output")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    settings = Settings()
    settings.offline = args.offline or settings.offline
    if args.data_dir:
        settings.data_dir = args.data_dir
    if args.output:
        settings.output_path = args.output
    settings.research_verbose = settings.research_verbose and not args.quiet
    stocks = args.stocks
    if stocks is None:
        path = Path(settings.watchlist_file)
        stocks = []
        if path.exists():
            with path.open(newline="", encoding="utf-8-sig") as stream:
                stocks = [row["stock"] for row in csv.DictReader(stream)]
    stocks = DiscoveryResult(
        stocks=[s.strip().upper() for s in stocks], reasoning="Input watchlist"
    ).stocks
    as_of = (
        datetime.fromisoformat(args.as_of.replace("Z", "+00:00"))
        if args.as_of
        else datetime.now(UTC)
    )
    request = RunRequest(
        watchlist=stocks, market=args.market, max_stocks=args.max_stocks, as_of=as_of
    )
    rows = asyncio.run(execute(request, settings))
    print("Completed " + str(len(rows)) + " stock predictions. See " + settings.output_path)


def plot():
    from stock_research.flow.master import StockResearchFlow

    StockResearchFlow(RunRequest(as_of=datetime.now(UTC)), None).plot("stock_flow")


if __name__ == "__main__":
    kickoff()
