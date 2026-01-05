import os
from langchain_openai import ChatOpenAI
from .config import get_settings

settings = get_settings()

class LLMFactory:
    @staticmethod
    def get_llm():
        """
        返回兼容 CrewAI 的 LangChain Chat 对象。
        使用通用的 OpenAI 兼容配置（适用于 OpenAI, 阿里云等）。
        """
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY 未设置")

        # 设置环境变量，以便其他可能隐式使用这些变量的库（如 CrewAI 的某些组件）能正常工作
        # NOTE: Explicitly map LLM_ vars to OPENAI_ vars for the LLM context.
        os.environ["OPENAI_API_KEY"] = settings.LLM_API_KEY
        if settings.LLM_API_BASE:
            os.environ["OPENAI_API_BASE"] = settings.LLM_API_BASE
            os.environ["OPENAI_BASE_URL"] = settings.LLM_API_BASE
        
        # NOTE: Do NOT set Embedding variables here to avoid pollution.
        # os.environ["OPENAI_EMBEDDING_MODEL"] = settings.EMBEDDING_MODEL

        return ChatOpenAI(
            openai_api_key=settings.LLM_API_KEY,
            openai_api_base=settings.LLM_API_BASE,
            model_name=settings.LLM_MODEL,
            temperature=0.1
        )

llm_factory = LLMFactory()
