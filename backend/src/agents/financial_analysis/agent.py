from crewai import Agent, Crew, Process, Task
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from pathlib import Path
import os
from src.core.llm_factory import llm_factory
from src.agents.base_agent import AgentConfigLoader
from src.tools.financial_table_tool import FinancialTableTool

from src.core.config import get_settings

# ==============================================================================
# Monkey Patching moved to src/core/patch.py
# ==============================================================================

class FinancialAnalysisCrew:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.agents_config, self.tasks_config = AgentConfigLoader.load_configs(Path(__file__).parent)
        self.llm = llm_factory.get_llm()

    def run(self) -> str:
        settings = get_settings()
        
        # Ensure we have a valid API Base for embeddings
        embedding_api_base = settings.EMBEDDING_API_BASE or settings.LLM_API_BASE
        embedding_api_key = settings.EMBEDDING_API_KEY or settings.LLM_API_KEY
        embedding_model = settings.EMBEDDING_MODEL
        
        print(f"DEBUG: Using Embedding API Base: {embedding_api_base}")
        print(f"DEBUG: Using Embedding Model: {embedding_model}")

        # FORCE Environment variables for Embeddings logic in Patch
        # Strict separation: Use EMBEDDING_ prefix which our patch prioritizes
        if embedding_api_key:
            os.environ["EMBEDDING_API_KEY"] = embedding_api_key
        if embedding_api_base:
            os.environ["EMBEDDING_API_BASE"] = embedding_api_base
        if embedding_model:
            os.environ["EMBEDDING_MODEL"] = embedding_model
        
        # Legacy/Support if patch checks this too (it does)
        os.environ["OPENAI_EMBEDDING_MODEL"] = embedding_model 


        # 1. "定位表格" 的知识源 (语义搜索)
        # Rely on "knowledge" -> "uploads/knowledge" symlink
        path_obj = Path(self.file_path)
        
        knowledge_source = PDFKnowledgeSource(file_paths=[path_obj.name])
        
        # 2. "提取表格" 的工具
        table_tool = FinancialTableTool()

        # 3. 创建 Agent
        financial_analyst = Agent(
            config=self.agents_config['financial_analyst'],
            llm=self.llm,
            knowledge_sources=[knowledge_source],
            tools=[table_tool],
            verbose=True,
            embedder={
                "provider": "openai",
                "config": {
                    "model": settings.EMBEDDING_MODEL,
                    "api_key": embedding_api_key,
                    "api_base": embedding_api_base
                }
            }
        )

        # 4. 创建任务
        locate_task = Task(
            config=self.tasks_config['locate_financial_tables'],
            agent=financial_analyst,
            guardrail="每一个数字都必须有原文依据，严禁产生幻觉或臆想。"
        )
        
        extract_task = Task(
            config=self.tasks_config['extract_financial_data'],
            agent=financial_analyst,
            context=[locate_task] # 传递定位任务的结果
        )


        # 5. 创建 Crew
        crew = Crew(
            agents=[financial_analyst],
            tasks=[locate_task, extract_task],
            process=Process.sequential,
            verbose=True
        )

        # 6. 启动
        result = crew.kickoff(inputs={'file_path': self.file_path})
        return result
