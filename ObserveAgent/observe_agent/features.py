"""Incident-scoped feature extraction / ETL."""

from __future__ import annotations

from datetime import timedelta

import httpx

from .models import Incident, IncidentFeatures, MetricFeature
from .telemetry import MetricSource


class IncidentFeatureExtractor:
    """Extract a small, explainable feature vector from Prometheus.

    Raw telemetry remains in Prometheus. Only the query, current value, baseline, and delta are
    persisted with the incident so a reviewer can reproduce every feature.
    """

    def __init__(self, metrics: MetricSource, baseline_offset_minutes: int = 30) -> None:
        self.metrics = metrics
        self.baseline_offset = timedelta(minutes=baseline_offset_minutes)

    def extract(self, incident: Incident) -> IncidentFeatures:
        service = incident.service
        expressions = {
            "request_rate_rps": (f'sum(rate(api_requests_total{{service="{service}"}}[5m]))'),
            "error_rate_ratio": (
                f'sum(rate(api_requests_total{{service="{service}",status=~"5.."}}[5m])) '
                f'/ clamp_min(sum(rate(api_requests_total{{service="{service}"}}[5m])), 0.001)'
            ),
            "p95_latency_seconds": (
                "histogram_quantile(0.95, sum by(le) "
                f'(rate(api_request_duration_seconds_bucket{{service="{service}"}}[5m])))'
            ),
        }
        values: dict[str, MetricFeature] = {}
        missing: list[str] = []
        baseline_at = incident.started_at - self.baseline_offset
        for name, query in expressions.items():
            try:
                current = self.metrics.instant_value(query, incident.started_at)
                baseline = self.metrics.instant_value(query, baseline_at)
            except (httpx.HTTPError, RuntimeError, ValueError):
                # One unavailable backend lowers confidence; it does not crash the incident.
                current = baseline = None
                missing.append(f"prometheus:{name}")
            delta = None if current is None or baseline is None else current - baseline
            values[name] = MetricFeature(
                name=name,
                current=current,
                baseline=baseline,
                delta=delta,
                query=query,
            )
            if current is None and f"prometheus:{name}" not in missing:
                missing.append(f"prometheus:{name}")
        return IncidentFeatures(
            incident_id=incident.id,
            window_start=incident.started_at - timedelta(minutes=15),
            window_end=incident.started_at + timedelta(minutes=5),
            values=values,
            context={
                "tenant_id": incident.tenant_id,
                "service": incident.service,
                "environment": incident.environment,
                "region": incident.region,
                "route": incident.route or "unknown",
                **incident.labels,
            },
            missing_sources=missing,
        )
