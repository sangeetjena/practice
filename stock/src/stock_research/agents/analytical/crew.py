"""YAML-backed analytical group using CrewAI's classic project decorators."""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, llm, task, tool

from stock_research.models.prediction import (
    AgentNote,
    AnalysisPrediction,
)


@CrewBase
class AnalyticalCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, model, tools, verbose=True):
        self.model, self.tools, self.verbose = model, tools, verbose

    @llm
    def agent_llm(self):
        return self.model

    @tool
    def volume_tool(self):
        return self.tools["volume"]

    @agent
    def volume(self):
        return Agent(config={**self.agents_config["volume"], "verbose": self.verbose})

    @task
    def volume_task(self):
        return Task(
            config=self.tasks_config["volume_task"],
            output_pydantic=AnalysisPrediction,
            guardrail=self.tools["volume"].output_guardrail(AnalysisPrediction),
        )

    @tool
    def candlestick_tool(self):
        return self.tools["candlestick"]

    @agent
    def candlestick(self):
        return Agent(config={**self.agents_config["candlestick"], "verbose": self.verbose})

    @task
    def candlestick_task(self):
        return Task(
            config=self.tasks_config["candlestick_task"],
            output_pydantic=AnalysisPrediction,
            guardrail=self.tools["candlestick"].output_guardrail(AnalysisPrediction),
        )

    @tool
    def bollinger_tool(self):
        return self.tools["bollinger"]

    @agent
    def bollinger(self):
        return Agent(config={**self.agents_config["bollinger"], "verbose": self.verbose})

    @task
    def bollinger_task(self):
        return Task(
            config=self.tasks_config["bollinger_task"],
            output_pydantic=AnalysisPrediction,
            guardrail=self.tools["bollinger"].output_guardrail(AnalysisPrediction),
        )

    @agent
    def assembly(self):
        return Agent(config={**self.agents_config["assembly"], "verbose": self.verbose})

    @task
    def assembly_task(self):
        return Task(config=self.tasks_config["assembly_task"], output_pydantic=AgentNote)

    @crew
    def crew(self):
        return Crew(
            agents=[self.volume(), self.candlestick(), self.bollinger(), self.assembly()],
            tasks=[
                self.volume_task(),
                self.candlestick_task(),
                self.bollinger_task(),
                self.assembly_task(),
            ],
            process=Process.sequential,
            memory=False,
            cache=False,
            verbose=self.verbose,
            tracing=False,
        )
