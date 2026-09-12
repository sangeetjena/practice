"""FastAPI webhook that turns incidents or Alertmanager alerts into triage reports."""

from __future__ import annotations

import hashlib
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException

from .agent import ReflexionAgent
from .config import Settings
from .features import IncidentFeatureExtractor
from .knowledge import SQLiteKnowledgeStore
from .models import AlertmanagerWebhook, Incident, IncidentFeedback, TriageReport
from .telemetry import PrometheusMetricSource


def build_agent(settings: Settings) -> ReflexionAgent:
    settings.validate()
    store = SQLiteKnowledgeStore(settings.database_path)
    runbook = Path(__file__).resolve().parent.parent / "data" / "runbooks" / "commerce-latency.md"
    if runbook.exists() and not store.has_active_source("runbook:commerce-latency"):
        store.ingest(
            "runbook:commerce-latency",
            runbook.read_text(encoding="utf-8"),
            {
                "source_type": "runbook",
                "review_status": "approved",
                "tenant_scope": "global",
                "service": "all",
                "owner": "commerce-platform",
            },
        )
    metrics = PrometheusMetricSource(settings.prometheus_url, settings.query_timeout_seconds)
    return ReflexionAgent(
        IncidentFeatureExtractor(metrics, settings.baseline_offset_minutes),
        store,
        knowledge_limit=settings.knowledge_limit,
    )


def create_app(agent: ReflexionAgent | None = None, settings: Settings | None = None) -> FastAPI:
    configured = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.agent = agent or build_agent(configured)
        yield

    app = FastAPI(
        title="ObserveAgent",
        version="0.1.0",
        description="Incident-triggered, evidence-backed observability agent lab.",
        lifespan=lifespan,
    )

    @app.get("/health/live", tags=["health"])
    def live() -> dict[str, str]:
        return {"status": "live"}

    @app.post("/v1/incidents", response_model=TriageReport, tags=["incidents"])
    def create_incident(incident: Incident) -> TriageReport:
        return app.state.agent.handle_incident(incident)

    @app.get("/v1/incidents/{incident_id}/report", response_model=TriageReport, tags=["incidents"])
    def get_report(incident_id: str) -> TriageReport:
        report = app.state.agent.knowledge.get_report(incident_id)
        if report is None:
            raise HTTPException(status_code=404, detail="incident report not found")
        return report

    @app.post("/v1/incidents/{incident_id}/feedback", tags=["feedback"])
    def submit_feedback(incident_id: str, feedback: IncidentFeedback) -> dict[str, object]:
        try:
            chunk_ids = app.state.agent.apply_feedback(incident_id, feedback)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return {"recorded": True, "knowledge_updated": bool(chunk_ids), "chunk_ids": chunk_ids}

    @app.post("/v1/alerts", response_model=list[TriageReport], tags=["alerts"])
    def alertmanager_webhook(webhook: AlertmanagerWebhook) -> list[TriageReport]:
        reports: list[TriageReport] = []
        for alert in webhook.alerts:
            if alert.status != "firing":
                continue
            service = alert.labels.get("service", "unknown")
            fingerprint = hashlib.sha256(
                f"{service}:{alert.labels}:{alert.startsAt.isoformat()}".encode()
            ).hexdigest()[:20]
            incident = Incident(
                id=f"alert-{fingerprint}",
                tenant_id=alert.labels.get("tenant_id", "platform"),
                title=alert.annotations.get("summary", alert.labels.get("alertname", "Alert")),
                service=service,
                environment=alert.labels.get("environment", "production"),
                region=alert.labels.get("region", "unknown"),
                route=alert.labels.get("route"),
                severity=alert.labels.get("severity", "warning"),
                started_at=alert.startsAt,
                labels=alert.labels,
                annotations=alert.annotations,
            )
            reports.append(app.state.agent.handle_incident(incident))
        return reports

    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run("observe_agent.api:app", host="0.0.0.0", port=8090)


if __name__ == "__main__":
    run()
