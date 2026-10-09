"""YAML-backed learner group using CrewAI's classic project decorators."""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, llm, task, tool

from stock_research.models.prediction import (
    LearningResult,
)


@CrewBase
class LearnerCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, model, tools, verbose=True):
        self.model, self.tools, self.verbose = model, tools, verbose

    @llm
    def agent_llm(self):
        return self.model

    @tool
    def learner_tool(self):
        return self.tools["learner"]

    @agent
    def learner(self):
        return Agent(config={**self.agents_config["learner"], "verbose": self.verbose})

    @task
    def learner_task(self):
        return Task(
            config=self.tasks_config["learner_task"],
            output_pydantic=LearningResult,
            guardrail=self.tools["learner"].output_guardrail(LearningResult),
        )

    @crew
    def crew(self):
        return Crew(
            agents=[self.learner()],
            tasks=[self.learner_task()],
            process=Process.sequential,
            memory=False,
            cache=False,
            verbose=self.verbose,
            tracing=False,
        )
