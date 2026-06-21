"""
app/core/config.py
──────────────────
Centralised configuration loaded from environment variables / .env file.
All settings are validated by Pydantic at startup — the application will
fail fast if a required variable is missing or has the wrong type.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, List, Optional

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "ParkWise Command Center"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True
    SECRET_KEY: str = Field(min_length=32)

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_flag(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"debug", "development", "dev"}:
                return True
        return value

    # ── API ───────────────────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ── Database ──────────────────────────────────────────────────────────────
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "parkwise"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "parkwise_db"
    DATABASE_URL: Optional[str] = None

    # Connection pool
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    @model_validator(mode="after")
    def assemble_db_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+psycopg2://"
                f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}"
                f"/{self.POSTGRES_DB}"
            )
        return self

    # ── Directories ───────────────────────────────────────────────────────────
    DATA_DIR: Path = Path("./data")
    MODEL_DIR: Path = Path("./models")
    LOG_DIR: Path = Path("./logs")

    @model_validator(mode="after")
    def create_dirs(self) -> "Settings":
        for d in (self.DATA_DIR, self.MODEL_DIR, self.LOG_DIR):
            d.mkdir(parents=True, exist_ok=True)
        return self

    # ── ML / DBSCAN ───────────────────────────────────────────────────────────
    DBSCAN_EPS: float = Field(default=0.005, gt=0)           # ~500m in degrees
    DBSCAN_MIN_SAMPLES: int = Field(default=10, ge=2)
    EIS_NORMALIZATION: str = Field(default="percentile", pattern="^(percentile|minmax)$")

    # ── Forecasting ───────────────────────────────────────────────────────────
    FORECAST_HORIZON_DAYS: int = Field(default=1, ge=1, le=7)
    LIGHTGBM_NUM_LEAVES: int = Field(default=31, ge=10)
    LIGHTGBM_N_ESTIMATORS: int = Field(default=200, ge=50)

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = Field(default="json", pattern="^(json|text)$")
    LOG_FILE: Optional[Path] = None

    # ── Computed helpers ──────────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached Settings singleton.
    Use FastAPI's Depends(get_settings) for dependency injection,
    or import directly for non-request contexts (e.g., Alembic env.py).
    """
    return Settings()


# Module-level alias for convenience in non-DI contexts.
settings: Settings = get_settings()
