from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "API Interview Lab"
    app_env: str = "local"
    database_path: Path = Path("data/orders.db")
    log_level: str = "INFO"
    api_token: str | None = None

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            app_env=os.getenv("APP_ENV", "local"),
            database_path=Path(os.getenv("DATABASE_PATH", "data/orders.db")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            api_token=os.getenv("API_TOKEN") or None,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
