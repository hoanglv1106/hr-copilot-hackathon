
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables.
    Example: DATABASE_URL=postgresql://... python -m uvicorn app.main:app
    """
    
    # ========== DATABASE ==========
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/hr_copilot"
    )
    """PostgreSQL connection URL"""
    
    # ========== REDIS ==========
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379"
    )
    """Redis connection URL"""
    
    # ========== VECTOR DATABASE ==========
    QDRANT_URL: str = os.getenv(
        "QDRANT_URL",
        "http://localhost:6333"
    )
    """Qdrant vector database URL"""
    
    QDRANT_COLLECTION_NAME: str = os.getenv(
        "QDRANT_COLLECTION_NAME",
        "hr_policies"
    )
    """Qdrant collection name for HR documents"""
    
    # ========== LLM - GEMINI ==========
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    """Google Gemini API key for LLM"""
    
    GEMINI_MODEL: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )
    """Gemini model name"""
    
    GEMINI_EMBEDDING_MODEL: str = os.getenv(
        "GEMINI_EMBEDDING_MODEL",
        "models/embedding-001"
    )
    """Gemini embedding model name"""
    
    # ========== LLM - COHERE ==========
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY")
    """Cohere API key for reranking"""
    
    COHERE_RERANK_MODEL: str = os.getenv(
        "COHERE_RERANK_MODEL",
        "rerank-multilingual-v3.0"
    )
    """Cohere rerank model name"""
    
    # ========== LOGGING ==========
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    """Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"""
    
    # ========== APPLICATION ==========
    APP_NAME: str = "HR Copilot API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # ========== LLM CONTEXT ==========
    MAX_TOKENS_CONTEXT: int = int(os.getenv("MAX_TOKENS_CONTEXT", "4096"))
    """Maximum tokens for context window in LLM"""
    
    # ========== FRONTEND ==========
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    """Frontend application URL"""
    
    class Config:
        """Pydantic settings config"""
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  


# Create global settings instance
settings = Settings()

