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
    database_url: str = "postgresql+asyncpg://stock:stock@localhost:5432/stock"
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"


def get_settings() -> Settings:
    return Settings()
