"""Local contention experiment, not a production capacity claim."""

import argparse
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from tagging_service import Database, ResourceKey, TaggingService


def main() -> None:
    """Run concurrent SQLite attachments and print measured latency/counts.

    Called by: command-line entry point.
    Returns: None; prints JSON and checks acknowledged writes.
    Example: python benchmark.py --requests 200 --workers 8.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if not 1 <= args.requests <= 100000 or not 1 <= args.workers <= 64:
        parser.error("requests must be 1..100000; workers must be 1..64")
    with TemporaryDirectory(prefix="tagging-benchmark-") as directory:
        database = Database(Path(directory) / "benchmark.sqlite3")
        database.initialize()
        service = TaggingService(database, "benchmark")
        tag = service.create_tag("shared")

        def attach(index):
            """Time one resource attachment and capture SQLite operational failure.

            Called by: main through ThreadPoolExecutor.map.
            Returns: (elapsed_seconds, success_boolean).
            Example: attach(7) attaches issue 7 to the benchmark tag.
            """
            start = perf_counter()
            try:
                service.attach_tag(ResourceKey("jira", "issue", str(index)), tag.tag_id)
                success = True
            except sqlite3.OperationalError:
                success = False
            return perf_counter() - start, success

        start = perf_counter()
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(attach, range(args.requests)))
        elapsed = perf_counter() - start
        durations = sorted(duration * 1000 for duration, _ in results)
        successful = sum(success for _, success in results)
        with database.transaction() as connection:
            stored = connection.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
        assert successful == stored, "acknowledged writes must match stored assignments"
        print(
            json.dumps(
                {
                    "workload": "unique-resource attachment to one shared tag",
                    "requests": args.requests,
                    "workers": args.workers,
                    "successful": successful,
                    "database_errors": args.requests - successful,
                    "elapsed_seconds": round(elapsed, 3),
                    "successful_operations_per_second": round(successful / elapsed, 1),
                    "operation_p50_ms": round(durations[len(durations) // 2], 2),
                    "operation_p95_ms": round(
                        durations[min(len(durations) - 1, int(len(durations) * 0.95))],
                        2,
                    ),
                    "latency_scope": "connection, lock wait and transaction; excludes executor queue time",
                    "sqlite_version": sqlite3.sqlite_version,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
