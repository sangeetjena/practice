from datetime import UTC, datetime, timedelta

from observe_agent.features import IncidentFeatureExtractor
from observe_agent.models import Incident


class SequenceMetrics:
    def __init__(self, values):
        self.values = iter(values)
        self.queries = []

    def instant_value(self, query, at):
        self.queries.append((query, at))
        value = next(self.values)
        if isinstance(value, Exception):
            raise value
        return value


def incident():
    return Incident(
        id="inc-1",
        tenant_id="acme",
        title="Orders latency",
        service="orders",
        started_at=datetime(2026, 9, 12, 8, tzinfo=UTC),
    )


def test_extracts_current_baseline_delta_and_reproducible_queries():
    metrics = SequenceMetrics([100, 80, 0.08, 0.01, 0.9, 0.2])

    features = IncidentFeatureExtractor(metrics, baseline_offset_minutes=30).extract(incident())

    assert features.values["request_rate_rps"].delta == 20
    assert features.values["error_rate_ratio"].current == 0.08
    assert features.values["p95_latency_seconds"].delta == 0.7
    assert all('service="orders"' in item.query for item in features.values.values())
    assert metrics.queries[0][1] - metrics.queries[1][1] == timedelta(minutes=30)
    assert features.missing_sources == []


def test_backend_failure_becomes_missing_evidence():
    metrics = SequenceMetrics([RuntimeError("down"), 80, 0.01, 0.01, 0.2, 0.2])

    features = IncidentFeatureExtractor(metrics).extract(incident())

    assert features.values["request_rate_rps"].current is None
    assert "prometheus:request_rate_rps" in features.missing_sources
