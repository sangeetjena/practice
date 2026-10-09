"""YAML-backed critique group using CrewAI's classic project decorators."""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, llm, task, tool

from stock_research.models.prediction import (
    CritiqueResult,
)


@CrewBase
class CritiqueCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, model, tools, verbose=True):
        self.model, self.tools, self.verbose = model, tools, verbose

    @llm
    def agent_llm(self):
        return self.model

    @tool
    def critique_tool(self):
        return self.tools["critique"]

    @agent
    def critique(self):
        return Agent(config={**self.agents_config["critique"], "verbose": self.verbose})

    @task
    def critique_task(self):
        return Task(
            config=self.tasks_config["critique_task"],
            output_pydantic=CritiqueResult,
            guardrail=self.tools["critique"].output_guardrail(CritiqueResult),
        )

    @crew
    def crew(self):
        return Crew(
            agents=[self.critique()],
            tasks=[self.critique_task()],
            process=Process.sequential,
            memory=False,
            cache=False,
            verbose=self.verbose,
            tracing=False,
        )
