"""
CompliScan LM — Application Configuration.
"""

from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from shared.domain.constants import (
    QUALITY_ASSESSMENT_VERSION,
    QUALITY_MIN_WIDTH,
    QUALITY_MIN_HEIGHT,
    QUALITY_MIN_PIXELS,
    QUALITY_BLUR_THRESHOLD,
    QUALITY_MIN_BRIGHTNESS,
    QUALITY_MAX_BRIGHTNESS,
    QUALITY_MIN_CONTRAST,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core
    APP_NAME: str = "CompliScan LM"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Security / Auth
    SECRET_KEY: str = "compliscan_mvp_development_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./compliscan.db"
    SYNC_DATABASE_URL: str = "sqlite:///./compliscan.db"

    # Supabase (Production Identity & Storage)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_AUTH_AUDIENCE: str = "authenticated"
    SUPABASE_STORAGE_BUCKET: str = "compliscan-evidence"
    STORAGE_BACKEND: str = "local"  # "local" or "supabase"

    # Local storage fallback
    LOCAL_STORAGE_DIR: str = "backend/uploads"

    # Worker / Analysis Job Configuration
    WORKER_LEASE_SECONDS: int = 60
    WORKER_POLL_INTERVAL_SECONDS: float = 2.0
    WORKER_MAX_JOB_ATTEMPTS: int = 3

    # Gemini Semantic Extraction Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"


    # Image Quality Assessment — Environment Overrides with Canonical Defaults
    # Canonical defaults live in shared.domain.constants. Precedence: ENV VAR > shared constants.
    QUALITY_VERSION: str = QUALITY_ASSESSMENT_VERSION
    QUALITY_MIN_WIDTH: int = QUALITY_MIN_WIDTH
    QUALITY_MIN_HEIGHT: int = QUALITY_MIN_HEIGHT
    QUALITY_MIN_PIXELS: int = QUALITY_MIN_PIXELS
    QUALITY_BLUR_THRESHOLD: float = QUALITY_BLUR_THRESHOLD
    QUALITY_MIN_BRIGHTNESS: float = QUALITY_MIN_BRIGHTNESS
    QUALITY_MAX_BRIGHTNESS: float = QUALITY_MAX_BRIGHTNESS
    QUALITY_MIN_CONTRAST: float = QUALITY_MIN_CONTRAST

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["*"]


settings = Settings()
