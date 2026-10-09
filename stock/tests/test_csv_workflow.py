import asyncio
import csv
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from stock_research.config import Settings
from stock_research.main import execute
from stock_research.models.market import Bar, FundamentalData, StockSnapshot
from stock_research.models.prediction import (
    AnalysisBundle,
    LearningResult,
    MasterPrediction,
    ResearchRow,
)
from stock_research.tools.csv_memory import CsvMemory, month_later
from stock_research.tools.market import MarketTools
from stock_research.tools.offline import OfflineMarketTools
from stock_research.tools.review import evaluate, learning_packet

NOW = datetime(2026, 10, 6, 20, tzinfo=timezone.utc)


def settings(tmp_path):
    return Settings(
        _env_file=None,
        data_dir=str(tmp_path / "data"),
        output_path=str(tmp_path / "output.md"),
        offline=True,
        research_verbose=False,
    )


async def snapshot(tmp_path, when=NOW):
    tools = OfflineMarketTools(settings(tmp_path), CsvMemory(tmp_path / "memory"))
    technical, fundamental, earnings, news = await asyncio.gather(
        *(getattr(tools, r)("IBM", when) for r in ["technical", "fundamental", "earnings", "news"])
    )
    return StockSnapshot(
        date=when,
        stock="IBM",
        technical=technical,
        fundamental=fundamental,
        earnings=earnings,
        news=news,
    )


def row(value, prediction="UP"):
    return ResearchRow(
        snapshot=value,
        analytical=AnalysisBundle(),
        master=MasterPrediction(
            stock="IBM", prediction=prediction, reasoning="test", confidence=0.5
        ),
        learning=LearningResult(stock="IBM", summary="test"),
    )


def test_calendar_month_cache_and_future_exclusion(tmp_path):
    store = CsvMemory(tmp_path)
    fetched = datetime(2026, 1, 31, 12, tzinfo=timezone.utc)
    value = FundamentalData(stock="IBM", fetched_at=fetched, source="test", indicators={"pe": 20})
    store.save_fundamentals(value)
    assert month_later(fetched) == datetime(2026, 2, 28, 12, tzinfo=timezone.utc)
    assert store.cached_fundamentals("IBM", datetime(2026, 2, 27, 12, tzinfo=timezone.utc)) == value
    assert store.cached_fundamentals("IBM", month_later(fetched)) is None
    assert store.cached_fundamentals("IBM", fetched - timedelta(seconds=1)) is None
    assert store.cached_fundamentals("OTHER", fetched) is None


def test_fundamental_tool_uses_memory_then_refreshes(tmp_path):
    async def run():
        store = CsvMemory(tmp_path)
        value = FundamentalData(stock="IBM", fetched_at=NOW, source="test", indicators={"pe": 20})
        store.save_fundamentals(value)
        tools = MarketTools(Settings(_env_file=None, alpha_vantage_api_key=None), store)
        calls = []
        tools._info = lambda stock: calls.append(stock) or {"trailingPE": 21}
        assert await tools.fundamental("IBM", NOW + timedelta(days=1)) == value
        refreshed = await tools.fundamental("IBM", month_later(NOW))
        assert refreshed.indicators["pe"] == 21 and calls == ["IBM"]

    asyncio.run(run())


def test_csv_roundtrip_preserves_predictions_and_quotes(tmp_path):
    value = row(asyncio.run(snapshot(tmp_path)))
    value.master.reasoning = 'Reason, with "quotes"\nand newline'
    store = CsvMemory(tmp_path / "output")
    store.save(value)
    assert store.rows() == [value]
    changed = value.model_copy(deep=True)
    changed.master.prediction = "DOWN"
    with pytest.raises(ValueError, match="immutable"):
        store.save(changed)
    with store.path.open(newline="", encoding="utf-8") as stream:
        raw = list(csv.DictReader(stream))
    assert raw[0]["master_reasoning"] == value.master.reasoning
    assert "bollinger_prediction" in raw[0] and "critique_date" in raw[0]


def test_outcome_uses_first_later_bar_and_waits_for_weekend(tmp_path):
    original = asyncio.run(snapshot(tmp_path))
    record = row(original)
    assert evaluate(record, original) is None
    current = asyncio.run(snapshot(tmp_path, NOW + timedelta(days=3)))
    outcome = evaluate(record, current)
    first = min(
        (b for b in current.technical.bars if b.bar_time > original.technical.bars[-1].bar_time),
        key=lambda b: b.bar_time,
    )
    assert outcome.actual_price == first.close
    assert outcome.actual_return == pytest.approx(
        first.close / original.technical.current_price - 1
    )
    abstained = row(original, "INSUFFICIENT_EVIDENCE")
    assert evaluate(abstained, current).verdict == "INCONCLUSIVE"


def test_learning_excludes_future_and_abstained_outcomes(tmp_path):
    original = asyncio.run(snapshot(tmp_path))
    current = asyncio.run(snapshot(tmp_path, NOW + timedelta(days=2)))
    record = row(original)
    record.outcome = evaluate(record, current)
    assert learning_packet([record], "IBM", NOW)["evaluated_count"] == 0
    assert learning_packet([record], "OTHER", current.date)["evaluated_count"] == 0
    assert learning_packet([record], "IBM", current.date)["evaluated_count"] == 1
    record.outcome.verdict = "INCONCLUSIVE"
    assert learning_packet([record], "IBM", current.date)["accuracy"] is None


def test_invalid_prices_and_incomplete_snapshot_rejected(tmp_path):
    with pytest.raises(ValidationError):
        Bar(bar_time=NOW, open=100, high=99, low=95, close=98, volume=10)
    with pytest.raises(ValidationError):
        Bar(bar_time=NOW, open=100, high=101, low=99, close=float("nan"), volume=10)


def test_full_flow_csv_memory_two_days_without_db_or_online_calls(tmp_path, monkeypatch):
    from stock_research.models.prediction import RunRequest

    async def forbidden(*args, **kwargs):
        raise AssertionError("Online provider must not be called")

    for name in ["technical", "fundamental", "news", "earnings", "discover"]:
        monkeypatch.setattr(MarketTools, name, forbidden)

    async def run():
        config = settings(tmp_path)
        first = await execute(RunRequest(watchlist=["IBM"], as_of=NOW), config)
        second = await execute(RunRequest(watchlist=["IBM"], as_of=NOW + timedelta(days=2)), config)
        assert first[0].master.prediction == second[0].master.prediction == "INSUFFICIENT_EVIDENCE"
        memory = CsvMemory(Path(config.data_dir) / "offline")
        records = memory.rows()
        assert len(records) == 2
        assert records[0].outcome.verdict == "INCONCLUSIVE"
        assert records[0].critique and records[1].outcome is None
        assert (memory.root / "ingestion.csv").exists()
        assert second[0].snapshot.fundamental.fetched_at == NOW
        assert "Run completed" in Path(config.output_path).read_text()
        assert not any(name.startswith("stock_research.tools.db.") for name in sys.modules)

    asyncio.run(run())


def test_live_replay_rejected_before_provider_calls(tmp_path):
    from stock_research.models.prediction import RunRequest

    config = settings(tmp_path)
    config.offline = False
    with pytest.raises(ValueError, match="Historical replay"):
        asyncio.run(execute(RunRequest(watchlist=["IBM"], as_of=NOW - timedelta(days=100)), config))


def test_snapshot_rejects_cross_stock_and_future_news(tmp_path):
    from stock_research.models.market import Article

    value = asyncio.run(snapshot(tmp_path))
    data = value.model_dump()
    data["fundamental"]["stock"] = "OTHER"
    with pytest.raises(ValidationError, match="Cross-stock"):
        StockSnapshot.model_validate(data)
    data = value.model_dump()
    data["news"]["articles"] = [
        Article(title="future", published_at=NOW + timedelta(days=1)).model_dump()
    ]
    with pytest.raises(ValidationError, match="News follows"):
        StockSnapshot.model_validate(data)
