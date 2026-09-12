"""Read-only adapters for observability backends."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

import httpx


class MetricSource(Protocol):
    def instant_value(self, query: str, at: datetime) -> float | None:
        """Return one scalar-like value for a PromQL expression."""


class PrometheusMetricSource:
    """Small Prometheus HTTP API client used by feature extraction.

    The caller supplies expressions built from validated identifiers. The adapter is read-only and
    deliberately returns ``None`` when a query has no series.
    """

    def __init__(self, base_url: str, timeout_seconds: float = 5) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def instant_value(self, query: str, at: datetime) -> float | None:
        with httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            trust_env=False,
        ) as client:
            response = client.get(
                "/api/v1/query",
                params={"query": query, "time": at.timestamp()},
            )
            response.raise_for_status()
            payload = response.json()
        if payload.get("status") != "success":
            raise RuntimeError(f"Prometheus query failed: {payload.get('error', 'unknown error')}")
        result = payload.get("data", {}).get("result", [])
        if not result:
            return None
        values = [float(item["value"][1]) for item in result if "value" in item]
        return sum(values) if values else None
