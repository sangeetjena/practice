"""Crew execution boundary. YAML owns tasks; typed source functions own facts."""

import json
from datetime import timedelta
from pathlib import Path

from crewai import LLM

from stock_research.agents.analytical.crew import AnalyticalCrew
from stock_research.agents.critique.crew import CritiqueCrew
from stock_research.agents.data_ingestion.crew import DataIngestionCrew
from stock_research.agents.learner.crew import LearnerCrew
from stock_research.agents.master.crew import MasterCrew
from stock_research.models.market import DiscoveryResult, StockSnapshot
from stock_research.models.prediction import (
    AnalysisBundle,
    AnalysisPrediction,
    CritiqueInput,
    CritiqueResult,
    LearningInput,
    LearningResult,
    MasterInput,
    MasterPrediction,
)
from stock_research.tools.agent_tool import BoundTool


class CrewExecutor:
    """Construct bound tools for each group; enforce source scope after agent output."""

    def __init__(self, settings, market, memory):
        self.settings, self.market, self.memory = settings, market, memory
        self.report = Path(settings.output_path)
        self.report.parent.mkdir(parents=True, exist_ok=True)
        self.report.write_text(
            "# Stock workflow execution\n\n"
            + ("SYNTHETIC OFFLINE TEST\n" if settings.offline else "Live agent run\n"),
            encoding="utf-8",
        )

    def log(self, stage, value):
        if hasattr(value, "model_dump"):
            value = value.model_dump(mode="json")
        with self.report.open("a", encoding="utf-8") as stream:
            stream.write(
                "\n## "
                + stage
                + "\n\n```json\n"
                + json.dumps(value, default=str, indent=2)
                + "\n```\n"
            )
        if self.settings.research_verbose:
            print("[stock] " + stage)

    def llm(self):
        return LLM(
            model=self.settings.research_llm,
            base_url=self.settings.research_llm_base_url,
            temperature=0,
            timeout=90,
        )

    def tool(self, name, loader):
        return BoundTool(name=name + "_tool", loader=loader)

    def evidence(self, name, value):
        async def load():
            return value

        return self.tool(name, load)

    async def call(self, crew, tools):
        await crew.akickoff()
        for name, tool in tools.items():
            if not tool.called:
                raise ValueError(name + " agent did not call its tool")
            self.log(name + " tool result", tool.result)
        for task in crew.tasks:
            if not task.output or task.output.pydantic is None:
                raise ValueError("Agent output failed structured validation")
            self.log(task.name or "agent result", task.output.pydantic)

    async def discovery(self, request):
        stocks = await self.market.discover(request)
        if self.settings.offline:
            result = DiscoveryResult(stocks=stocks, reasoning="Synthetic watchlist")
        else:
            tools = self.ingestion_tools("", request.as_of)
            tools["discovery"] = self.evidence(
                "discovery", {"stocks": stocks, "market": request.market}
            )
            definition = DataIngestionCrew(self.llm(), tools, self.settings.research_verbose)
            crew = definition.discovery_crew()
            await self.call(crew, {"discovery": tools["discovery"]})
            result = crew.tasks[0].output.pydantic
        if not set(result.stocks) <= set(stocks):
            raise ValueError("Discovery invented stocks")
        self.log("Discovery", result)
        return result.stocks[: request.max_stocks]

    def ingestion_tools(self, stock, as_of):
        tools = {"discovery": self.evidence("discovery", {})}
        for role in ["technical", "fundamental", "earnings", "news"]:

            async def load(role=role):
                return await getattr(self.market, role)(stock, as_of)

            tools[role] = self.tool(role, load)
        return tools

    async def ingestion(self, stock, as_of):
        import asyncio

        tools = self.ingestion_tools(stock, as_of)
        roles = ["technical", "fundamental", "earnings", "news"]
        if self.settings.offline:
            await asyncio.gather(*(tools[r]._arun() for r in roles))
            news = tools["news"].result
        else:
            crew = DataIngestionCrew(self.llm(), tools, self.settings.research_verbose).crew()
            await self.call(crew, {r: tools[r] for r in roles})
            for role, task in zip(roles, crew.tasks[:4]):
                actual = task.output.pydantic
                expected = tools[role].result
                if role == "news":
                    if actual.model_copy(update={"summary": expected.summary}) != expected:
                        raise ValueError("News agent altered sourced articles")
                elif actual != expected:
                    raise ValueError(role + " agent altered source values")
            news = crew.tasks[3].output.pydantic
        result = StockSnapshot(
            date=as_of,
            stock=stock,
            technical=tools["technical"].result,
            fundamental=tools["fundamental"].result,
            earnings=tools["earnings"].result,
            news=news,
        )
        self.log("Ingestion snapshot", result)
        return result

    async def analysis(self, snapshot):
        roles = ["volume", "candlestick", "bollinger"]
        if self.settings.offline:
            predictions = [
                AnalysisPrediction(
                    stock=snapshot.stock,
                    specialty=r,
                    prediction="INSUFFICIENT_EVIDENCE",
                    reasoning="Synthetic data cannot support a real recommendation.",
                )
                for r in roles
            ]
        else:
            tools = {r: self.evidence(r, snapshot) for r in roles}
            crew = AnalyticalCrew(self.llm(), tools, self.settings.research_verbose).crew()
            await self.call(crew, tools)
            predictions = [t.output.pydantic for t in crew.tasks[:3]]
        for role, prediction in zip(roles, predictions):
            if prediction.stock != snapshot.stock or prediction.specialty != role:
                raise ValueError("Analytical output outside assigned scope")
            if not snapshot.technical.indicators.get("ready"):
                prediction.prediction = "INSUFFICIENT_EVIDENCE"
                prediction.reasoning = "Insufficient completed technical history."
        result = AnalysisBundle(predictions=predictions)
        self.log("Specialist predictions", result)
        return result

    async def review(self, row, snapshot, outcome):
        if self.settings.offline:
            result = CritiqueResult(
                prediction_id=row.prediction_id,
                suggestion="Synthetic review; do not infer real lessons.",
            )
        else:
            horizon_end = outcome.target_bar_time + timedelta(hours=24)
            # Later news outside the scored interval cannot explain that outcome.
            later = {
                "bars": [
                    b.model_dump(mode="json")
                    for b in snapshot.technical.bars
                    if row.snapshot.technical.bars[-1].bar_time
                    < b.bar_time
                    <= outcome.target_bar_time
                ],
                "news": [
                    a.model_dump(mode="json")
                    for a in snapshot.news.articles
                    if row.snapshot.date < a.published_at <= horizon_end
                ],
                "fundamentals": snapshot.fundamental.model_dump(mode="json")
                if row.snapshot.date < snapshot.fundamental.fetched_at <= horizon_end
                else None,
            }
            packet = CritiqueInput(
                original_prediction=row.master,
                original_snapshot=row.snapshot,
                later_evidence=later,
                objective_outcome=outcome,
            )
            tools = {"critique": self.evidence("critique", packet)}
            crew = CritiqueCrew(self.llm(), tools, self.settings.research_verbose).crew()
            await self.call(crew, tools)
            result = crew.tasks[0].output.pydantic
        if result.prediction_id != row.prediction_id:
            raise ValueError("Critique cited another prediction")
        self.log("Critique", result)
        return result

    async def learn(self, packet):
        packet = LearningInput.model_validate(packet).model_dump(mode="json")
        if self.settings.offline:
            result = LearningResult(
                stock=packet["stock"], summary="Synthetic historical learning", lessons=[]
            )
        else:
            tools = {"learner": self.evidence("learner", packet)}
            crew = LearnerCrew(self.llm(), tools, self.settings.research_verbose).crew()
            await self.call(crew, tools)
            result = crew.tasks[0].output.pydantic
        if result.stock != packet["stock"]:
            raise ValueError("Learner returned another stock")
        self.log("Learner", result)
        return result

    async def master(self, snapshot, analysis, lessons):
        knowledge_path = Path(self.settings.knowledge_file)
        knowledge = knowledge_path.read_text(encoding="utf-8") if knowledge_path.exists() else ""
        if self.settings.offline:
            result = MasterPrediction(
                stock=snapshot.stock,
                prediction="INSUFFICIENT_EVIDENCE",
                confidence=0,
                reasoning="Synthetic offline run; no actual market recommendation.",
            )
        else:
            packet = MasterInput(
                snapshot=snapshot, analytical=analysis, learner=lessons, knowledge=knowledge
            )
            tools = {"master": self.evidence("master", packet)}
            crew = MasterCrew(self.llm(), tools, self.settings.research_verbose).crew()
            await self.call(crew, tools)
            result = crew.tasks[0].output.pydantic
        if result.stock != snapshot.stock:
            raise ValueError("Master returned another stock")
        if not snapshot.technical.indicators.get("ready"):
            result.prediction = "INSUFFICIENT_EVIDENCE"
            result.confidence = 0
            result.reasoning = "Insufficient completed technical history."
        self.log("Master prediction", result)
        return result
