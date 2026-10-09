"""Individual group Flows call their YAML-backed crews through a typed executor."""

from crewai.flow.flow import Flow, start

from stock_research.tools.review import evaluate, learning_packet


class DataIngestionFlow(Flow):
    def __init__(self, executor, stock, as_of):
        super().__init__(tracing=False)
        self.executor, self.stock, self.as_of = executor, stock, as_of

    @start()
    async def run_ingestion(self):
        snapshot = await self.executor.ingestion(self.stock, self.as_of)
        self.executor.memory.save_snapshot(snapshot)
        return snapshot


class AnalyticalFlow(Flow):
    def __init__(self, executor, snapshot):
        super().__init__(tracing=False)
        self.executor, self.snapshot = executor, snapshot

    @start()
    async def run_analysis(self):
        return await self.executor.analysis(self.snapshot)


class CritiqueFlow(Flow):
    def __init__(self, executor, snapshot):
        super().__init__(tracing=False)
        self.executor, self.snapshot = executor, snapshot

    @start()
    async def review_history(self):
        for row in self.executor.memory.rows():
            if row.outcome:
                continue
            outcome = evaluate(row, self.snapshot)
            if not outcome:
                continue
            critique = await self.executor.review(row, self.snapshot, outcome)
            row.outcome, row.critique = outcome, critique
            self.executor.memory.save(row)


class LearnerFlow(Flow):
    def __init__(self, executor, snapshot):
        super().__init__(tracing=False)
        self.executor, self.snapshot = executor, snapshot

    @start()
    async def learn_history(self):
        packet = learning_packet(
            self.executor.memory.rows(), self.snapshot.stock, self.snapshot.date
        )
        return await self.executor.learn(packet)


class MasterPredictionFlow(Flow):
    """The master group combines typed specialist and learner outputs."""

    def __init__(self, executor, snapshot, analysis, lessons):
        super().__init__(tracing=False)
        self.executor, self.snapshot, self.analysis, self.lessons = (
            executor,
            snapshot,
            analysis,
            lessons,
        )

    @start()
    async def predict(self):
        return await self.executor.master(self.snapshot, self.analysis, self.lessons)
