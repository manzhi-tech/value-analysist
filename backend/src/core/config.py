from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    ENV: str = "development"
    PROJECT_NAME: str = "Value Analyst"
    
    # 数据库
    DATABASE_URL: str = "sqlite:///./value_analyst.db"
    
    # ChromaDB (向量数据库)
    CHROMA_SERVER_HOST: str = "localhost"
    CHROMA_SERVER_HTTP_PORT: int = 8000
    
    # LLM Configuration (OpenAI Compatible)
    LLM_API_KEY: str | None = None
    LLM_API_BASE: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4"
    
    # Embedding Configuration
    EMBEDDING_API_KEY: str | None = None
    EMBEDDING_API_BASE: str | None = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    class Config:
        env_file = (".env", "../.env")
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
