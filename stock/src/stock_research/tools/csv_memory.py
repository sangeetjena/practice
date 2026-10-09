"""CSV is the first-version durable memory. No database connection is made here."""

import calendar
import csv
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from filelock import FileLock

from stock_research.models.market import FundamentalData
from stock_research.models.prediction import ResearchRow


def month_later(value):
    """Calendar-month expiry handles short months and year boundaries."""
    year, month = (value.year + 1, 1) if value.month == 12 else (value.year, value.month + 1)
    return value.replace(
        year=year, month=month, day=min(value.day, calendar.monthrange(year, month)[1])
    )


class CsvMemory:
    """Atomic writes protected by a file lock; safe across local scheduler processes."""

    def __init__(self, directory):
        csv.field_size_limit(8 * 1024 * 1024)
        self.root = Path(directory)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "stock_memory.csv"
        self.fundamentals = self.root / "fundamentals.csv"

    def _read(self, path):
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))

    def _write(self, path, rows):
        if not rows:
            return
        fields = list(rows[0])
        with NamedTemporaryFile(
            mode="w", newline="", encoding="utf-8", dir=self.root, delete=False
        ) as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
            temporary = Path(stream.name)
        try:
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)

    def rows(self):
        with FileLock(str(self.path) + ".lock"):
            return [ResearchRow.model_validate_json(row["record"]) for row in self._read(self.path)]

    def save(self, row):
        """Update only this prediction ID; preserve all earlier master predictions."""
        with FileLock(str(self.path) + ".lock"):
            existing = self._read(self.path)
            updated = self.flatten(row)
            for index, item in enumerate(existing):
                if item["prediction_id"] == str(row.prediction_id):
                    original = ResearchRow.model_validate_json(item["record"])
                    if original.master != row.master or original.snapshot != row.snapshot:
                        raise ValueError("Original prediction and evidence are immutable")
                    existing[index] = updated
                    break
            else:
                existing.append(updated)
            self._write(self.path, existing)

    def save_snapshot(self, snapshot):
        """Persist source ingestion even before analytical/master stages run."""
        path = self.root / "ingestion.csv"
        with FileLock(str(path) + ".lock"):
            rows = self._read(path)
            rows.append(
                {
                    "date": snapshot.date.isoformat(),
                    "stock": snapshot.stock,
                    "current_price": snapshot.technical.current_price,
                    "record": snapshot.model_dump_json(),
                }
            )
            self._write(path, rows)

    def flatten(self, row):
        snapshot = row.snapshot
        output = {
            "prediction_id": str(row.prediction_id),
            "date": snapshot.date.isoformat(),
            "stock": snapshot.stock,
            "current_price": snapshot.technical.current_price,
            "technical_indicators": json.dumps(snapshot.technical.indicators),
            "fundamental_indicators": json.dumps(snapshot.fundamental.indicators),
            "fundamental_fetched_at": snapshot.fundamental.fetched_at.isoformat(),
            "news": snapshot.news.summary,
            "earnings": snapshot.earnings.model_dump_json(),
        }
        for key in [
            "rsi14",
            "volume",
            "volume_ratio20",
            "bollinger_upper",
            "bollinger_middle",
            "bollinger_lower",
        ]:
            output[key] = snapshot.technical.indicators.get(key)
        for key in ["pe", "market_cap", "eps", "debt_to_equity"]:
            output[key] = snapshot.fundamental.indicators.get(key)
        by_name = {p.specialty: p for p in row.analytical.predictions}
        for name in ["volume", "candlestick", "bollinger"]:
            p = by_name.get(name)
            output[name + "_prediction"] = p.prediction if p else ""
            output[name + "_reasoning"] = p.reasoning if p else ""
        output.update(
            {
                "master_prediction": row.master.prediction,
                "master_reasoning": row.master.reasoning,
                "master_confidence": row.master.confidence,
                "learner_lessons": json.dumps(row.learning.lessons),
                "critique_verdict": row.outcome.verdict if row.outcome else "",
                "critique_suggestion": row.critique.suggestion if row.critique else "",
                "critique_date": row.outcome.evaluated_at.isoformat() if row.outcome else "",
                "actual_return": row.outcome.actual_return if row.outcome else "",
                "record": row.model_dump_json(),
            }
        )
        return output

    def cached_fundamentals(self, stock, as_of):
        with FileLock(str(self.fundamentals) + ".lock"):
            values = [
                FundamentalData.model_validate_json(row["record"])
                for row in self._read(self.fundamentals)
            ]
        eligible = [
            v
            for v in values
            if v.stock == stock and v.fetched_at <= as_of < month_later(v.fetched_at)
        ]
        return max(eligible, key=lambda v: v.fetched_at) if eligible else None

    def save_fundamentals(self, value):
        with FileLock(str(self.fundamentals) + ".lock"):
            rows = self._read(self.fundamentals)
            rows.append(
                {
                    "stock": value.stock,
                    "fetched_at": value.fetched_at.isoformat(),
                    "record": value.model_dump_json(),
                }
            )
            self._write(self.fundamentals, rows)
