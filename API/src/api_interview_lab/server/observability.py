from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

REQUESTS = Counter(
    "api_http_requests_total",
    "Total HTTP requests",
    ("method", "route", "status"),
)
LATENCY = Histogram(
    "api_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ("method", "route"),
)
IN_FLIGHT = Gauge("api_http_requests_in_flight", "HTTP requests currently running")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(payload)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)


def install_observability(app: FastAPI) -> None:
    @app.middleware("http")
    async def metrics_and_request_id(request: Request, call_next: Any) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        started = time.perf_counter()
        IN_FLIGHT.inc()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            route = request.scope.get("route")
            route_label = getattr(route, "path_format", request.url.path)
            elapsed = time.perf_counter() - started
            REQUESTS.labels(request.method, route_label, str(status_code)).inc()
            LATENCY.labels(request.method, route_label).observe(elapsed)
            IN_FLIGHT.dec()

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
