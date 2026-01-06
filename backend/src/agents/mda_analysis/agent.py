from crewai import Agent, Crew, Process, Task
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from pathlib import Path
import os
from src.core.llm_factory import llm_factory
from src.agents.base_agent import AgentConfigLoader

class MDACrew:
    def __init__(self, file_paths: list[str]):
        self.file_paths = file_paths
        self.agents_config, self.tasks_config = AgentConfigLoader.load_configs(Path(__file__).parent)
        self.llm = llm_factory.get_llm()

    def run(self) -> str:
        knowledge_source = PDFKnowledgeSource(file_paths=self.file_paths)

        mda_analyst = Agent(
            config=self.agents_config['mda_analyst'],
            llm=self.llm,
            knowledge_sources=[knowledge_source],
            verbose=True
        )

        analysis_task = Task(
            config=self.tasks_config['analyze_mda_risks'],
            agent=mda_analyst,
            guardrail="每一句话都必须有原文依据，严禁产生幻觉或臆想。报告必须全中文。引用格式必须为 [[Page X]]。"
        )

        crew = Crew(
            agents=[mda_analyst],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result
