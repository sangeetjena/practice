"""Top-level orchestration: discovery â†’ ingestion â†’ critique â†’ learner â†’ analysis â†’ master."""

from crewai.flow.flow import Flow, listen, start

from stock_research.flow.groups import (
    AnalyticalFlow,
    CritiqueFlow,
    DataIngestionFlow,
    LearnerFlow,
    MasterPredictionFlow,
)
from stock_research.models.prediction import ResearchRow, RunState


class StockResearchFlow(Flow[RunState]):
    def __init__(self, request, executor):
        super().__init__(tracing=False)
        self.request, self.executor = request, executor
        self.stocks = []
        self.snapshots = []
        self.lessons = {}
        self.analysis = {}

    @start()
    async def discover(self):
        self.stocks = await self.executor.discovery(self.request)

    @listen(discover)
    async def ingest(self):
        for stock in self.stocks:
            snapshot = await DataIngestionFlow(
                self.executor, stock, self.request.as_of
            ).kickoff_async()
            self.snapshots.append(snapshot)

    @listen(ingest)
    async def critique(self):
        for snapshot in self.snapshots:
            await CritiqueFlow(self.executor, snapshot).kickoff_async()

    @listen(critique)
    async def learn(self):
        for snapshot in self.snapshots:
            self.lessons[snapshot.stock] = await LearnerFlow(
                self.executor, snapshot
            ).kickoff_async()

    @listen(learn)
    async def analyze(self):
        for snapshot in self.snapshots:
            self.analysis[snapshot.stock] = await AnalyticalFlow(
                self.executor, snapshot
            ).kickoff_async()

    @listen(analyze)
    async def predict(self):
        for snapshot in self.snapshots:
            master = await MasterPredictionFlow(
                self.executor, snapshot, self.analysis[snapshot.stock], self.lessons[snapshot.stock]
            ).kickoff_async()
            row = ResearchRow(
                snapshot=snapshot,
                master=master,
                analytical=self.analysis[snapshot.stock],
                learning=self.lessons[snapshot.stock],
            )
            self.executor.memory.save(row)
            self.state.rows.append(row)
        self.executor.log(
            "Run completed", {"rows": len(self.state.rows), "csv": str(self.executor.memory.path)}
        )
        return self.state.rows
