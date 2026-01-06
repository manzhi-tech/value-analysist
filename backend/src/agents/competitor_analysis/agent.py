from crewai import Agent, Crew, Process, Task
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from pathlib import Path
import os
from src.core.llm_factory import llm_factory
from src.agents.base_agent import AgentConfigLoader

class CompetitorCrew:
    def __init__(self, file_paths: list[str]):
        self.file_paths = file_paths
        self.agents_config, self.tasks_config = AgentConfigLoader.load_configs(Path(__file__).parent)
        self.llm = llm_factory.get_llm()

    def run(self) -> str:
        # Re-use the same knowledge source logic
        filenames = [Path(p).name for p in self.file_paths]
        knowledge_source = PDFKnowledgeSource(file_paths=filenames)

        competitor_analyst = Agent(
            config=self.agents_config['competitor_analyst'],
            llm=self.llm,
            knowledge_sources=[knowledge_source],
            verbose=True
        )

        analysis_task = Task(
            config=self.tasks_config['compare_competitors'],
            agent=competitor_analyst,
            guardrail="每一句话都必须有原文依据，严禁产生幻觉或臆想。报告必须全中文。引用格式必须为 [[Page X]]。"
        )

        crew = Crew(
            agents=[competitor_analyst],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result
