from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SIH OCR Service"
    VERSION: str = "0.1.0"
    PORT: int = 8001
    
    class Config:
        env_file = ".env"

settings = Settings()
