from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = "sk-or-v1-0000000000000000000000000000000000000000000000000000000000000000"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/news_digest_db"
    SECRET_KEY: str = "change_this_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FRONTEND_BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()