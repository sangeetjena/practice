"""Exercise real YAML-backed CrewAI crews with mocked LLM task execution."""

import asyncio
import json
import threading
from datetime import datetime, timezone

import pytest
from crewai import LLM, Task
from crewai.tasks.task_output import TaskOutput

from stock_research.config import Settings
from stock_research.flow.executor import CrewExecutor
from stock_research.models.prediction import AgentNote, AnalysisPrediction
from stock_research.tools.agent_tool import BoundTool
from stock_research.tools.csv_memory import CsvMemory
from stock_research.tools.offline import OfflineMarketTools

NOW = datetime(2026, 10, 6, 20, tzinfo=timezone.utc)


def test_real_ingestion_crew_runs_four_branches_concurrently_then_barrier(tmp_path, monkeypatch):
    config = Settings(
        _env_file=None,
        output_path=str(tmp_path / "output.md"),
        offline=False,
        research_verbose=False,
    )
    market = OfflineMarketTools(config, CsvMemory(tmp_path / "csv"))
    executor = CrewExecutor(config, market, market.memory)
    monkeypatch.setattr(
        CrewExecutor, "llm", lambda self: LLM(model="openai/gpt-4o-mini", api_key="test-not-used")
    )
    barrier = threading.Barrier(4, timeout=10)
    finished = set()
    lock = threading.Lock()

    def mock_task(self, agent, context, tools):
        role = agent.role
        if role == "assembly":
            assert finished == {"technical", "fundamental", "earnings", "news"}
            result = AgentNote(summary="all source branches completed")
        else:
            barrier.wait()  # Fails if the crew accidentally serializes the branches.
            adapter = agent.tools[0]
            adapter._run()
            result = adapter.result
            if role == "news":
                result = result.model_copy(update={"summary": "Synthetic news summary"})
            with lock:
                finished.add(role)
        output = TaskOutput(
            description=self.description, agent=role, pydantic=result, raw=result.model_dump_json()
        )
        self.output = output
        return output

    async def mock_async(self, agent, context, tools):
        return await asyncio.to_thread(mock_task, self, agent, context, tools)

    monkeypatch.setattr(Task, "_aexecute_core", mock_async)
    monkeypatch.setattr(Task, "_execute_core", mock_task)
    snapshot = asyncio.run(executor.ingestion("IBM", NOW))
    assert snapshot.news.summary == "Synthetic news summary"
    assert snapshot.technical.current_price == snapshot.technical.bars[-1].close


def test_analytical_crew_concurrent_specialists_and_scope_validation(tmp_path, monkeypatch):
    from stock_research.models.market import StockSnapshot

    config = Settings(
        _env_file=None, output_path=str(tmp_path / "output.md"), research_verbose=False
    )
    memory = CsvMemory(tmp_path / "csv")
    market = OfflineMarketTools(config, memory)
    executor = CrewExecutor(config, market, memory)
    monkeypatch.setattr(
        CrewExecutor, "llm", lambda self: LLM(model="openai/gpt-4o-mini", api_key="test-not-used")
    )

    async def make_snapshot():
        values = await asyncio.gather(
            *(
                getattr(market, r)("IBM", NOW)
                for r in ["technical", "fundamental", "earnings", "news"]
            )
        )
        return StockSnapshot(
            date=NOW,
            stock="IBM",
            **dict(zip(["technical", "fundamental", "earnings", "news"], values)),
        )

    snapshot = asyncio.run(make_snapshot())
    barrier = threading.Barrier(3, timeout=10)
    finished = set()

    def mock_task(self, agent, context, tools):
        role = agent.role
        if role == "assembly":
            assert len(finished) == 3
            result = AgentNote(summary="done")
        else:
            barrier.wait()
            agent.tools[0]._run()
            finished.add(role)
            result = AnalysisPrediction(
                stock="IBM", specialty=role, prediction="UP", reasoning="fixture"
            )
        self.output = TaskOutput(
            description=self.description, agent=role, pydantic=result, raw=result.model_dump_json()
        )
        return self.output

    async def mock_async(self, agent, context, tools):
        return await asyncio.to_thread(mock_task, self, agent, context, tools)

    monkeypatch.setattr(Task, "_aexecute_core", mock_async)
    monkeypatch.setattr(Task, "_execute_core", mock_task)
    result = asyncio.run(executor.analysis(snapshot))
    assert {r.specialty for r in result.predictions} == {"volume", "candlestick", "bollinger"}


def test_bound_tool_caches_extraction_and_rejects_agent_inputs():
    from pydantic import ValidationError

    calls = []

    async def load():
        calls.append(1)
        return {"stock": "IBM"}

    tool = BoundTool(name="test_tool", loader=load)

    async def run():
        assert json.loads(await tool._arun()) == {"stock": "IBM"}
        await tool._arun()

    asyncio.run(run())
    assert calls == [1]
    with pytest.raises(ValidationError):
        tool.args_schema.model_validate({"url": "https://example.com"})


@pytest.mark.parametrize("failure", ["missing_tool", "altered_source", "invalid_json"])
def test_ingestion_guardrail_recovers_before_assembly(tmp_path, monkeypatch, failure):
    """Use real CrewAI task validation/retry, replacing only the model execution."""
    from crewai import Agent

    config = Settings(
        _env_file=None, output_path=str(tmp_path / "output.md"), research_verbose=False
    )
    memory = CsvMemory(tmp_path / "csv")
    market = OfflineMarketTools(config, memory)
    executor = CrewExecutor(config, market, memory)
    monkeypatch.setattr(
        CrewExecutor, "llm", lambda self: LLM(model="openai/gpt-4o-mini", api_key="test-not-used")
    )
    attempts = {}

    async def mock_model(self, task, context=None, tools=None):
        role = self.role
        attempts[role] = attempts.get(role, 0) + 1
        if role == "assembly":
            assert attempts["fundamental"] == 2
            return AgentNote(summary="all validated")
        adapter = self.tools[0]
        if role == "fundamental" and attempts[role] == 1:
            if failure == "missing_tool":
                return '{"fabricated": true}'
            await adapter._arun()
            if failure == "invalid_json":
                return "not JSON"
            altered = adapter.result.model_copy(update={"indicators": {"pe": 999}})
            return altered.model_dump_json()
        if role == "fundamental":
            assert "fundamental_tool" in context
        await adapter._arun()
        return adapter.result

    monkeypatch.setattr(Agent, "aexecute_task", mock_model)
    snapshot = asyncio.run(executor.ingestion("IBM", NOW))
    assert attempts["fundamental"] == 2
    assert snapshot.fundamental == asyncio.run(market.fundamental("IBM", NOW))
    assert attempts["assembly"] == 1


def test_missing_tool_guardrail_exhausts_bounded_retries(monkeypatch):
    """Repeated fabricated responses must fail without executing the loader."""
    from crewai import Agent

    from stock_research.models.market import FundamentalData

    calls = []

    async def loader():
        raise AssertionError("The agent never called this loader")

    adapter = BoundTool(name="fundamental_tool", loader=loader)
    agent = Agent(
        role="fundamental",
        goal="Read source",
        backstory="test",
        tools=[adapter],
        llm=LLM(model="openai/gpt-4o-mini", api_key="test-not-used"),
        verbose=False,
    )
    task = Task(
        description="Read fundamentals",
        expected_output="FundamentalData",
        agent=agent,
        output_pydantic=FundamentalData,
        guardrail=adapter.output_guardrail(FundamentalData),
        guardrail_max_retries=2,
    )

    async def skip_tool(self, task, context=None, tools=None):
        calls.append(context)
        return FundamentalData(stock="IBM", fetched_at=NOW, source="invented", indicators={})

    monkeypatch.setattr(Agent, "aexecute_task", skip_tool)
    with pytest.raises(Exception, match="after 2 retries"):
        asyncio.run(task.aexecute_sync(agent=agent))
    assert len(calls) == 3
    assert not adapter.called
