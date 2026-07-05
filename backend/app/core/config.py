# pyrefly: ignore [missing-import]
from pydantic import field_validator
from pydantic_settings import BaseSettings
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "ChatMinds API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkey-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: str | list[str] = ["http://localhost:5173", "http://localhost", "http://localhost:8080"]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            try:
                return json.loads(v)
            except ValueError:
                return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
