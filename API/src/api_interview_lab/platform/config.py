"""Explicit settings: demo credentials are generated, never silently enabled."""
import json
import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    service: str = field(default_factory=lambda: os.getenv("SERVICE_NAME", "orders"))
    database_url: str = field(default_factory=lambda: os.getenv(
        "DATABASE_URL", "sqlite:///./platform.db"))
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", ""))
    cursor_secret: str = field(default_factory=lambda: os.getenv("CURSOR_SECRET", ""))
    credentials: dict = field(default_factory=lambda: json.loads(os.getenv("CREDENTIALS_JSON", "{}")))
    root_path: str = field(default_factory=lambda: os.getenv("ROOT_PATH", ""))
    issuer: str = "api-interview-lab"
    audience: str = "commerce-api"
    customers_url: str = field(default_factory=lambda: os.getenv(
        "CUSTOMERS_URL", "http://localhost:8002"))
    fault_delay_ms: int = field(default_factory=lambda: int(os.getenv("FAULT_DELAY_MS", "0")))
    fault_fail: bool = field(default_factory=lambda: os.getenv("FAULT_FAIL", "false") == "true")
    telemetry: bool = field(default_factory=lambda: os.getenv("OTEL_ENABLED", "false") == "true")

    def validate(self):
        if self.service not in {"orders", "customers", "products"}:
            raise ValueError("SERVICE_NAME must be orders, customers, or products")
        if min(len(self.jwt_secret), len(self.cursor_secret)) < 32:
            raise ValueError("JWT_SECRET and CURSOR_SECRET must each be at least 32 characters")
