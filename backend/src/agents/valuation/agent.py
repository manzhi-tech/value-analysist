from crewai import Agent, Crew, Process, Task
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from pathlib import Path
import os
from src.core.config import get_settings
from src.core.llm_factory import llm_factory
from src.agents.base_agent import AgentConfigLoader
from src.tools.dcf_calculator_tool import DCFCalculatorTool

class ValuationCrew:
    def __init__(self, financial_data: dict, moat_rating: str, file_paths: list[str] = None):
        self.financial_data = financial_data
        self.moat_rating = moat_rating
        self.file_paths = file_paths or []
        self.agents_config, self.tasks_config = AgentConfigLoader.load_configs(Path(__file__).parent)
        self.llm = llm_factory.get_llm()

    def run(self) -> str:
        # 0. Tool & Knowledge
        dcf_tool = DCFCalculatorTool()
        
        # Configure Knowledge Source
        knowledge_sources = []
        if self.file_paths:
            settings = get_settings()
            # Ensure embedding config is set (similar to BusinessAnalysisCrew)
            embedding_api_key = settings.EMBEDDING_API_KEY or settings.LLM_API_KEY
            embedding_api_base = settings.EMBEDDING_API_BASE or settings.LLM_API_BASE
            embedding_model = settings.EMBEDDING_MODEL
            
            # Set env vars for compatibility
            if embedding_api_key: os.environ["EMBEDDING_API_KEY"] = embedding_api_key
            if embedding_api_base: os.environ["EMBEDDING_API_BASE"] = embedding_api_base
            if embedding_model: os.environ["EMBEDDING_MODEL"] = embedding_model
            os.environ["OPENAI_EMBEDDING_MODEL"] = embedding_model or "text-embedding-ada-002"

            embedder_config = {
                "provider": "openai",
                "config": {
                    "model": embedding_model,
                    "api_key": embedding_api_key,
                    "api_base": embedding_api_base
                }
            }
            
            # Verify paths
            valid_paths = []
            knowledge_root = Path("knowledge")
            for p in self.file_paths:
                full_path = knowledge_root / p
                if full_path.exists():
                    valid_paths.append(p)
            
            if valid_paths:
                knowledge_sources = [PDFKnowledgeSource(file_paths=valid_paths)]
        
        # 2. Agent
        valuation_expert = Agent(
            config=self.agents_config['valuation_expert'],
            llm=self.llm,
            tools=[dcf_tool],
            knowledge_sources=knowledge_sources,
            embedder=embedder_config if knowledge_sources else None,
            verbose=True
        )

        # 3. Task
        valuation_task = Task(
            config=self.tasks_config['calculate_intrinsic_value'],
            agent=valuation_expert,
            guardrail="每一句话都必须有原文依据，严禁产生幻觉或臆想。报告必须全中文。引用格式必须为 [[Page X]]。"
        )

        # 4. Crew
        crew = Crew(
            agents=[valuation_expert],
            tasks=[valuation_task],
            process=Process.sequential,
            verbose=True
        )

        # 5. Kickoff
        result = crew.kickoff(inputs={
            'financial_data': self.financial_data,
            'moat_rating': self.moat_rating
        })
        return result
