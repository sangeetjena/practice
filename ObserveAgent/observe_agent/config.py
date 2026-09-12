"""Environment-backed configuration for the observer service."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _csv(name: str, default: str = "") -> tuple[str, ...]:
    return tuple(item.strip() for item in os.getenv(name, default).split(",") if item.strip())


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
    embedding_provider: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_PROVIDER", "hash").lower()
    )
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    )
    embedding_dimensions: int = field(
        default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSIONS", "128"))
    )
    embedding_api_key: str | None = field(
        default_factory=lambda: os.getenv("EMBEDDING_API_KEY") or os.getenv("LLM_API_KEY")
    )
    embedding_base_url: str | None = field(
        default_factory=lambda: os.getenv("EMBEDDING_BASE_URL") or None
    )
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "rule").lower())
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-5-mini"))
    llm_api_key: str | None = field(default_factory=lambda: os.getenv("LLM_API_KEY"))
    llm_base_url: str | None = field(default_factory=lambda: os.getenv("LLM_BASE_URL") or None)
    llm_max_output_tokens: int = field(
        default_factory=lambda: int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "1600"))
    )
    llm_temperature: float | None = field(
        default_factory=lambda: (
            float(os.environ["LLM_TEMPERATURE"]) if os.getenv("LLM_TEMPERATURE") else None
        )
    )
    action_mode: str = field(default_factory=lambda: os.getenv("ACTION_MODE", "dry_run").lower())
    action_allowlist: tuple[str, ...] = field(default_factory=lambda: _csv("ACTION_ALLOWLIST"))
    http_allowed_hosts: tuple[str, ...] = field(default_factory=lambda: _csv("HTTP_ALLOWED_HOSTS"))
    github_allowed_repositories: tuple[str, ...] = field(
        default_factory=lambda: _csv("GITHUB_ALLOWED_REPOSITORIES")
    )
    email_allowed_recipients: tuple[str, ...] = field(
        default_factory=lambda: _csv("EMAIL_ALLOWED_RECIPIENTS")
    )
    action_min_confidence: float = field(
        default_factory=lambda: float(os.getenv("ACTION_MIN_CONFIDENCE", "0.7"))
    )
    github_token: str | None = field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))
    smtp_host: str | None = field(default_factory=lambda: os.getenv("SMTP_HOST"))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_username: str | None = field(default_factory=lambda: os.getenv("SMTP_USERNAME"))
    smtp_password: str | None = field(default_factory=lambda: os.getenv("SMTP_PASSWORD"))
    smtp_from: str | None = field(default_factory=lambda: os.getenv("SMTP_FROM"))

    def validate(self) -> None:
        if not self.prometheus_url.startswith(("http://", "https://")):
            raise ValueError("PROMETHEUS_URL must be HTTP or HTTPS")
        if not 0 < self.query_timeout_seconds <= 30:
            raise ValueError("OBSERVE_QUERY_TIMEOUT_SECONDS must be in (0, 30]")
        if not 1 <= self.baseline_offset_minutes <= 24 * 60:
            raise ValueError("OBSERVE_BASELINE_OFFSET_MINUTES must be in [1, 1440]")
        if not 1 <= self.knowledge_limit <= 20:
            raise ValueError("OBSERVE_KNOWLEDGE_LIMIT must be in [1, 20]")
        if self.embedding_provider not in {"hash", "openai"}:
            raise ValueError("EMBEDDING_PROVIDER must be hash or openai")
        if self.embedding_provider == "openai" and not self.embedding_api_key:
            raise ValueError("EMBEDDING_API_KEY or LLM_API_KEY is required for OpenAI embeddings")
        if self.embedding_dimensions < 16:
            raise ValueError("EMBEDDING_DIMENSIONS must be at least 16")
        if self.llm_provider not in {"rule", "openai"}:
            raise ValueError("LLM_PROVIDER must be rule or openai")
        if self.llm_provider == "openai" and not self.llm_api_key:
            raise ValueError("LLM_API_KEY is required for the OpenAI reasoner")
        if not 128 <= self.llm_max_output_tokens <= 32_768:
            raise ValueError("LLM_MAX_OUTPUT_TOKENS must be in [128, 32768]")
        if self.llm_temperature is not None and not 0 <= self.llm_temperature <= 2:
            raise ValueError("LLM_TEMPERATURE must be in [0, 2]")
        if self.action_mode not in {"dry_run", "execute"}:
            raise ValueError("ACTION_MODE must be dry_run or execute")
        if not 0 <= self.action_min_confidence <= 1:
            raise ValueError("ACTION_MIN_CONFIDENCE must be in [0, 1]")
