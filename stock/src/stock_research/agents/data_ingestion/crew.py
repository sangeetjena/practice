"""YAML-backed data_ingestion group using CrewAI's classic project decorators."""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, llm, task, tool

from stock_research.models.market import (
    DiscoveryResult,
    EarningsData,
    FundamentalData,
    NewsData,
    TechnicalData,
)
from stock_research.models.prediction import (
    AgentNote,
)


@CrewBase
class DataIngestionCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, model, tools, verbose=True):
        self.model, self.tools, self.verbose = model, tools, verbose

    @llm
    def agent_llm(self):
        return self.model

    @tool
    def discovery_tool(self):
        return self.tools["discovery"]

    @agent
    def discovery(self):
        return Agent(config={**self.agents_config["discovery"], "verbose": self.verbose})

    @task
    def discovery_task(self):
        return Task(
            config=self.tasks_config["discovery_task"],
            output_pydantic=DiscoveryResult,
            guardrail=self.tools["discovery"].output_guardrail(DiscoveryResult),
        )

    @tool
    def technical_tool(self):
        return self.tools["technical"]

    @agent
    def technical(self):
        return Agent(config={**self.agents_config["technical"], "verbose": self.verbose})

    @task
    def technical_task(self):
        return Task(
            config=self.tasks_config["technical_task"],
            output_pydantic=TechnicalData,
            guardrail=self.tools["technical"].output_guardrail(TechnicalData, exact_source=True),
        )

    @tool
    def fundamental_tool(self):
        return self.tools["fundamental"]

    @agent
    def fundamental(self):
        return Agent(config={**self.agents_config["fundamental"], "verbose": self.verbose})

    @task
    def fundamental_task(self):
        return Task(
            config=self.tasks_config["fundamental_task"],
            output_pydantic=FundamentalData,
            guardrail=self.tools["fundamental"].output_guardrail(
                FundamentalData, exact_source=True
            ),
        )

    @tool
    def earnings_tool(self):
        return self.tools["earnings"]

    @agent
    def earnings(self):
        return Agent(config={**self.agents_config["earnings"], "verbose": self.verbose})

    @task
    def earnings_task(self):
        return Task(
            config=self.tasks_config["earnings_task"],
            output_pydantic=EarningsData,
            guardrail=self.tools["earnings"].output_guardrail(EarningsData, exact_source=True),
        )

    @tool
    def news_tool(self):
        return self.tools["news"]

    @agent
    def news(self):
        return Agent(config={**self.agents_config["news"], "verbose": self.verbose})

    @task
    def news_task(self):
        return Task(
            config=self.tasks_config["news_task"],
            output_pydantic=NewsData,
            guardrail=self.tools["news"].output_guardrail(
                NewsData, exact_source=True, allow_summary=True
            ),
        )

    @agent
    def assembly(self):
        return Agent(config={**self.agents_config["assembly"], "verbose": self.verbose})

    @task
    def assembly_task(self):
        return Task(config=self.tasks_config["assembly_task"], output_pydantic=AgentNote)

    @crew
    def discovery_crew(self):
        return Crew(
            agents=[self.discovery()],
            tasks=[self.discovery_task()],
            process=Process.sequential,
            memory=False,
            cache=False,
            verbose=self.verbose,
            tracing=False,
        )

    @crew
    def crew(self):
        return Crew(
            agents=[
                self.technical(),
                self.fundamental(),
                self.earnings(),
                self.news(),
                self.assembly(),
            ],
            tasks=[
                self.technical_task(),
                self.fundamental_task(),
                self.earnings_task(),
                self.news_task(),
                self.assembly_task(),
            ],
            process=Process.sequential,
            memory=False,
            cache=False,
            verbose=self.verbose,
            tracing=False,
        )
