from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Legal Metrology Packaged Commodity Compliance System"
    API_V1_STR: str = "/api/v1"
    
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG: bool = False
    
    # Authentication
    SECRET_KEY: str = "a-very-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "raghav"
    POSTGRES_DB: str = "sih_db"
    POSTGRES_PORT: int = 5432
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
    @property
    def SYNC_SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # AI Service Configuration
    AI_SERVICE_URL: str = "http://localhost:8002"
    AI_CONNECT_TIMEOUT: float = 5.0
    AI_READ_TIMEOUT: float = 120.0
    MOCK_AI: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Image Upload Configuration
    UPLOAD_DIR: str = "uploads"
    @property
    def ABSOLUTE_UPLOAD_DIR(self) -> str:
        import os
        from pathlib import Path
        base_dir = Path(__file__).resolve().parent.parent.parent
        return str(base_dir / self.UPLOAD_DIR)
        
    MAX_IMAGE_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_IMAGE_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".webp"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
