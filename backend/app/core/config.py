import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Resume Analyzer"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "postgresql://resume_user:resume_pass@localhost:5432/resume_analyzer"

    FRONTEND_URL: str = "http://localhost:5173"

    MAX_UPLOAD_SIZE_MB: int = 5
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
