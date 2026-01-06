from crewai import Agent, Crew, Process, Task
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from pathlib import Path
import os
import logging
from src.core.llm_factory import llm_factory
from src.agents.base_agent import AgentConfigLoader
from src.core.config import get_settings

# ==============================================================================
# Monkey Patching moved to src/core/patch.py
# ==============================================================================

logger = logging.getLogger(__name__)

class BusinessAnalysisCrew:
    def __init__(self, file_paths: list[str]):
        self.file_paths = file_paths
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
        
        # 1. 设置知识源
        # Files are stored in "uploads/knowledge"
        # We have a symlink "knowledge" -> "uploads/knowledge" for CrewAI compatibility
        
        knowledge_dir = Path("uploads/knowledge")
        knowledge_dir.mkdir(parents=True, exist_ok=True)
            
        params_paths = []
        for p in self.file_paths:
            path_obj = Path(p)
            if not path_obj.exists():
                cleaned = p.strip('"\'')
                if Path(cleaned).exists():
                    path_obj = Path(cleaned)
                else:
                    logger.error(f"Original file not found: {p}")
                    continue
            
            # Determine if file is already in knowledge dir
            # resolve() handles absolute paths comparison
            if path_obj.parent.resolve() == knowledge_dir.resolve():
                # Already in the right place, just use the filename
                params_paths.append(path_obj.name)
            else:
                # Need to symlink/copy to knowledge dir
                target_link = knowledge_dir / path_obj.name
                try:
                    if target_link.exists():
                        target_link.unlink()
                    os.symlink(path_obj.absolute(), target_link)
                    logger.info(f"Symlinked {path_obj} to {target_link}")
                    params_paths.append(path_obj.name)
                except Exception as e:
                    logger.error(f"Failed to symlink {path_obj}: {e}")
                    import shutil
                    shutil.copy(path_obj, target_link)
                    params_paths.append(path_obj.name)

        if not params_paths:
            raise ValueError(f"No valid files to process. Inputs: {self.file_paths}")

        embedder_config = {
            "provider": "openai",
            "config": {
                "model": settings.EMBEDDING_MODEL,
                "api_key": embedding_api_key,
                "api_base": embedding_api_base
            }
        }
        logger.info(f"Using Embedder Config: {embedder_config}")

        knowledge_source = PDFKnowledgeSource(file_paths=params_paths)
        
        # 3. 创建 Agent
        business_analyst = Agent(
            config=self.agents_config['business_analyst'],
            llm=self.llm,
            knowledge_sources=[knowledge_source],
            verbose=True,
            embedder=embedder_config
        )

        # 4. 创建任务
        analysis_task = Task(
            config=self.tasks_config['analyze_business_model'],
            agent=business_analyst,
            guardrail="每一句话都必须有原文依据，严禁产生幻觉或臆想。"
        )

        # 5. 创建 Crew
        crew = Crew(
            agents=[business_analyst],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True
        )

        # 6. 启动
        result = crew.kickoff()
        return result
