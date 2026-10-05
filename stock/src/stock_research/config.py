"""Validated runtime configuration."""
from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class ExecutionMode(StrEnum):
    PAPER = "paper"
    HUMAN_APPROVED = "human_approved"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STOCK_", env_file=".env", extra="ignore")

    environment: str = "local"
    execution_mode: ExecutionMode = ExecutionMode.PAPER
    database_url: str | None = None
    timescale_url: str | None = None
    redis_url: str | None = None
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    alpha_vantage_api_key: str | None = None
    alpha_vantage_exchange_timezone: str = "America/New_York"
    alpha_vantage_full_history_enabled: bool = False
    alpha_vantage_intraday_enabled: bool = False
    alpha_vantage_interval: str = "5min"
    alpha_vantage_poll_seconds: int = 300
    log_level: str = "INFO"


def get_settings() -> Settings:
    return Settings()
