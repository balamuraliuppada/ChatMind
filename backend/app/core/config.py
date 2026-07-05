# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ChatMinds API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkey-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
