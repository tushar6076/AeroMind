from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ======================
    # Project
    # ======================
    PROJECT_NAME: str = "AeroMind"
    ENVIRONMENT: str = "development"

    # ======================
    # Server
    # ======================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # ======================
    # Security
    # ======================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ======================
    # Database (Neon)
    # ======================
    DATABASE_URL: str
    DIRECT_URL: Optional[str] = None

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Convert DATABASE_URL to asyncpg format"""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL

    # ======================
    # Redis (Upstash)
    # ======================
    REDIS_URL: str

    # ======================
    # CORS
    # ======================
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            # Handle JSON-like string from .env
            import json
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # ======================
    # Email (SMTP)
    # ======================
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_FROM_NAME: Optional[str] = "AeroMind"
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: int = 587

    # ======================
    # AI Keys
    # ======================
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROK_API_KEY: Optional[str] = None

    # ======================
    # Admin
    # ======================
    ADMIN_EMAIL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()