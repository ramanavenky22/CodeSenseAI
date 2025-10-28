"""
Configuration settings for CodeSense AI
"""

from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    OPENAI_API_KEY: str
    GITHUB_TOKEN: str
    GITHUB_WEBHOOK_SECRET: str
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/codesense_ai"
    
    # Security
    SECRET_KEY: str
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # SonarQube (Optional)
    SONARQUBE_URL: Optional[str] = None
    SONARQUBE_TOKEN: Optional[str] = None
    
    # LangChain
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "codesense-ai"
    
    # Model Configuration
    DEFAULT_MODEL: str = "gpt-4"
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.1
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()