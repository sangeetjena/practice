from __future__ import annotations

import argparse
import csv
from pathlib import Path

from api_interview_lab.config import get_settings
from api_interview_lab.data.sqlite_repository import SQLiteOrderRepository
from api_interview_lab.patterns.pydantic_pattern import OrderPayload


def load_csv(csv_path: Path, repository: SQLiteOrderRepository) -> tuple[int, int]:
    inserted = skipped = 0
    with csv_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            payload = OrderPayload.model_validate(row)
            if repository.get(payload.id):
                skipped += 1
            else:
                repository.create(payload.to_domain())
                inserted += 1
    return inserted, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Load a local CSV feed into SQLite")
    parser.add_argument("--feed", type=Path, default=Path("feeds/orders.csv"))
    parser.add_argument("--database", type=Path, default=get_settings().database_path)
    args = parser.parse_args()
    inserted, skipped = load_csv(args.feed, SQLiteOrderRepository(args.database))
    print(f"Loaded {inserted} orders; skipped {skipped} existing orders")


if __name__ == "__main__":
    main()

