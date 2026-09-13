"""Cloud settings fail closed when durable storage or tenant configuration is missing.

Example: DATABASE_URL=postgresql+psycopg://... and OBSERVE_TENANTS supplies each
tenant's service ownership, Prometheus URL and action allowlists. See .env.cloud.example.
"""

import json
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class CloudSettings:
    database_url: str
    checkpoint_url: str
    auth_keys: str
    tenants: dict
    chroma_host: str
    chroma_port: int = 8000
    chroma_ssl: bool = False
    chroma_headers: str = "{}"
    topic: str = ""
    push_audience: str = ""
    push_service_account: str = ""
    scheduler_audience: str = ""
    scheduler_service_account: str = ""
    max_attempts: int = 5

    @classmethod
    def from_env(cls):
        database_url = os.environ["DATABASE_URL"]
        if not database_url.startswith("postgresql+psycopg://"):
            raise ValueError("cloud runtime requires PostgreSQL; SQLite is test-only")
        tenants = json.loads(os.environ["OBSERVE_TENANTS"])
        if not tenants:
            raise ValueError("at least one tenant must be configured")
        for tenant in tenants.values():
            if not tenant.get("services") or not tenant.get("prometheus_url"):
                raise ValueError("tenant needs services and a dedicated/scoped Prometheus URL")
        return cls(
            database_url=database_url,
            checkpoint_url=database_url.replace("postgresql+psycopg://", "postgresql://", 1),
            auth_keys=os.environ["OBSERVE_AUTH_KEYS"],
            tenants=tenants,
            chroma_host=os.environ["CHROMA_HOST"],
            chroma_port=int(os.getenv("CHROMA_PORT", "8000")),
            chroma_ssl=os.getenv("CHROMA_SSL", "false").lower() == "true",
            chroma_headers=os.getenv("CHROMA_HEADERS", "{}"),
            topic=os.getenv("PUBSUB_TOPIC", ""),
            push_audience=os.getenv("PUBSUB_AUDIENCE", ""),
            push_service_account=os.getenv("PUBSUB_SERVICE_ACCOUNT", ""),
            scheduler_audience=os.getenv("SCHEDULER_AUDIENCE", ""),
            scheduler_service_account=os.getenv("SCHEDULER_SERVICE_ACCOUNT", ""),
        )
