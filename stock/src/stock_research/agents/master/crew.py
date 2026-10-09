"""YAML-backed master group using CrewAI's classic project decorators."""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, llm, task, tool

from stock_research.models.prediction import (
    MasterPrediction,
)


@CrewBase
class MasterCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, model, tools, verbose=True):
        self.model, self.tools, self.verbose = model, tools, verbose

    @llm
    def agent_llm(self):
        return self.model

    @tool
    def master_tool(self):
        return self.tools["master"]

    @agent
    def master(self):
        return Agent(config={**self.agents_config["master"], "verbose": self.verbose})

    @task
    def master_task(self):
        return Task(
            config=self.tasks_config["master_task"],
            output_pydantic=MasterPrediction,
            guardrail=self.tools["master"].output_guardrail(MasterPrediction),
        )

    @crew
    def crew(self):
        return Crew(
            agents=[self.master()],
            tasks=[self.master_task()],
            process=Process.sequential,
            memory=False,
            cache=False,
            verbose=self.verbose,
            tracing=False,
        )
