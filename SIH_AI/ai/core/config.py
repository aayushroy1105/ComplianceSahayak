import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Legal Metrology AI Service"
    VERSION: str = "0.1.0"
    
    # Flags
    MOCK_AI: bool = False
    DEBUG_PIPELINE: bool = False
    
    # OCR Integration
    OCR_SERVICE_URL: str = "http://localhost:8001"
    OCR_TIMEOUT: int = 30
    
    # Paths
    LEGAL_RULES_PATH: str = "../legal_metrology_rules.md"
    
    # Future Placeholders
    OCR_MODEL: Optional[str] = None
    EMBEDDING_MODEL: Optional[str] = None
    LLM_MODEL: Optional[str] = None
    CHROMA_PATH: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
