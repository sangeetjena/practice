"""Environment-backed configuration for the observer service."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: Path = field(
        default_factory=lambda: Path(os.getenv("OBSERVE_DB_PATH", "./observe-agent.db"))
    )
    prometheus_url: str = field(
        default_factory=lambda: os.getenv("PROMETHEUS_URL", "http://localhost:9090")
    )
    query_timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("OBSERVE_QUERY_TIMEOUT_SECONDS", "5"))
    )
    baseline_offset_minutes: int = field(
        default_factory=lambda: int(os.getenv("OBSERVE_BASELINE_OFFSET_MINUTES", "30"))
    )
    knowledge_limit: int = field(
        default_factory=lambda: int(os.getenv("OBSERVE_KNOWLEDGE_LIMIT", "5"))
    )

    def validate(self) -> None:
        if not self.prometheus_url.startswith(("http://", "https://")):
            raise ValueError("PROMETHEUS_URL must be HTTP or HTTPS")
        if not 0 < self.query_timeout_seconds <= 30:
            raise ValueError("OBSERVE_QUERY_TIMEOUT_SECONDS must be in (0, 30]")
        if not 1 <= self.baseline_offset_minutes <= 24 * 60:
            raise ValueError("OBSERVE_BASELINE_OFFSET_MINUTES must be in [1, 1440]")
        if not 1 <= self.knowledge_limit <= 20:
            raise ValueError("OBSERVE_KNOWLEDGE_LIMIT must be in [1, 20]")
