"""REST surface for tenant-scoped asynchronous incidents and private worker delivery.

Example: POST /v1/incidents with X-API-Key + Idempotency-Key returns 202; polling
GET /v1/incidents/{id} reports completion. No model work runs after returning HTTP.
"""

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from ..models import AlertmanagerWebhook
from .config import CloudSettings
from .contracts import ApprovalInput, FeedbackInput, IncidentInput, MessageInput
from .database import Busy, Conflict, Database, fingerprint
from .security import Authenticator
from .transport import decode_event, verify_service_identity


def public_view(row):
    # Internal run IDs are exposed as opaque identifiers, never accepted as authorization.
    return {
        k: row.get(k)
        for k in ["id", "session_id", "run_id", "revision", "status", "result", "proposal_version"]
    }


def create_app(settings=None, db=None, worker=None, publisher=None, role="api"):
    @asynccontextmanager
    async def lifespan(app):
        configured = settings or CloudSettings.from_env()
        app.state.settings = configured
        app.state.db = db or Database(configured.database_url)
        if role == "api":
            app.state.auth = Authenticator(configured.auth_keys)
        else:
            from .runtime import GraphFactory, Worker
            from .transport import OutboxPublisher

            app.state.worker = worker or Worker(
                app.state.db, GraphFactory(configured, app.state.db)
            )
            app.state.publisher = publisher or OutboxPublisher(app.state.db, configured.topic)
        yield
        if db is None:
            app.state.db.engine.dispose()

    app = FastAPI(title=f"ObserveAgent cloud {role}", version="0.3.0", lifespan=lifespan)

    @app.exception_handler(Conflict)
    async def conflict_handler(request, error):
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @app.exception_handler(KeyError)
    async def missing_handler(request, error):
        return JSONResponse(status_code=404, content={"detail": "resource not found"})

    @app.middleware("http")
    async def bound_body(request, call_next):
        if request.method in {"POST", "PUT", "PATCH"}:
            # Stream cap also handles chunked requests without a Content-Length header.
            size, chunks = 0, []
            async for chunk in request.stream():
                size += len(chunk)
                if size > 65536:
                    return JSONResponse(status_code=413, content={"detail": "request too large"})
                chunks.append(chunk)
            request._body = b"".join(chunks)
        return await call_next(request)

    @app.get("/health/live")
    def live():
        return {"status": "live"}

    @app.get("/health/ready")
    def ready():
        from sqlalchemy import text

        with app.state.db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}

    def principal(
        x_api_key: str | None = Header(default=None),
        authorization: str | None = Header(default=None),
    ):
        key = x_api_key
        if not key and authorization and authorization.startswith("Bearer "):
            key = authorization[7:]
        value = app.state.auth.authenticate(key)
        if value.tenant_id not in app.state.settings.tenants:
            raise HTTPException(403, "tenant not configured")
        return value

    authenticated = Depends(principal)

    if role == "api":

        @app.post("/v1/incidents", status_code=202)
        def submit(
            body: IncidentInput,
            identity=authenticated,
            idempotency_key: str = Header(min_length=1, max_length=200),
        ):
            identity.require("submit")
            tenant = app.state.settings.tenants[identity.tenant_id]
            if body.service not in tenant["services"]:
                raise HTTPException(403, "service not owned by tenant")
            row = app.state.db.submit(
                identity.tenant_id,
                identity.subject,
                body.model_dump(mode="json"),
                idempotency_key,
                fingerprint(body.model_dump(mode="json", exclude_unset=True)),
            )
            return public_view(row)

        @app.get("/v1/incidents/{incident_id}")
        def status(incident_id: str, identity=authenticated):
            identity.require("read")
            return public_view(app.state.db.get(identity.tenant_id, incident_id))

        @app.get("/v1/incidents/{incident_id}/report")
        def report(incident_id: str, identity=authenticated):
            identity.require("read")
            row = app.state.db.get(identity.tenant_id, incident_id)
            if not row["result"] or not row["result"].get("report"):
                raise HTTPException(409, "report is not ready")
            return row["result"]["report"]

        @app.get("/v1/incidents/{incident_id}/messages")
        def history(incident_id: str, identity=authenticated):
            identity.require("read")
            return app.state.db.history(identity.tenant_id, incident_id)

        @app.post("/v1/incidents/{incident_id}/messages", status_code=202)
        def message(incident_id: str, body: MessageInput, identity=authenticated):
            identity.require("submit")
            return public_view(
                app.state.db.append(
                    identity.tenant_id, incident_id, identity.subject, "message", body.model_dump()
                )
            )

        @app.post("/v1/incidents/{incident_id}/actions/decision", status_code=202)
        def approval(incident_id: str, body: ApprovalInput, identity=authenticated):
            identity.require("review")
            return public_view(
                app.state.db.append(
                    identity.tenant_id, incident_id, identity.subject, "approval", body.model_dump()
                )
            )

        @app.post("/v1/incidents/{incident_id}/feedback", status_code=202)
        def feedback(incident_id: str, body: FeedbackInput, identity=authenticated):
            identity.require("review")
            return public_view(
                app.state.db.append(
                    identity.tenant_id, incident_id, identity.subject, "feedback", body.model_dump()
                )
            )

        @app.post("/v1/alerts", status_code=202)
        def alerts(body: AlertmanagerWebhook, identity=authenticated):
            identity.require("submit")
            allowed = app.state.settings.tenants[identity.tenant_id]["services"]
            firing = [alert for alert in body.alerts if alert.status == "firing"]
            for alert in firing:
                if alert.labels.get("service") not in allowed:
                    raise HTTPException(403, "alert service not owned by tenant")
                if alert.labels.get("tenant_id", identity.tenant_id) != identity.tenant_id:
                    raise HTTPException(403, "alert tenant mismatch")
            accepted = []
            for alert in firing:
                key = "alert-" + fingerprint([alert.labels, alert.startsAt.isoformat()])[:40]
                try:
                    row = app.state.db.get(identity.tenant_id, key)
                except KeyError:
                    incident = IncidentInput(
                        id=key,
                        title=alert.annotations.get("summary", "Firing alert"),
                        service=alert.labels["service"],
                        started_at=alert.startsAt,
                        annotations=alert.annotations,
                    )
                    row = app.state.db.submit(
                        identity.tenant_id,
                        identity.subject,
                        incident.model_dump(mode="json"),
                        key,
                        fingerprint([identity.tenant_id, key]),
                    )
                accepted.append(public_view(row))
            return accepted
    elif role == "worker":

        @app.post("/internal/events", status_code=204)
        async def deliver(request: Request, authorization: str | None = Header(default=None)):
            configured = app.state.settings
            # Validate Google-signed JWT audience and exact publisher service account.
            from starlette.concurrency import run_in_threadpool

            await run_in_threadpool(
                verify_service_identity,
                authorization,
                configured.push_audience,
                configured.push_service_account,
            )
            event_id = decode_event(await request.json())
            try:
                await run_in_threadpool(app.state.worker.process, event_id)
            except Busy as error:
                raise HTTPException(503, "incident busy; retry delivery") from error
            return Response(status_code=204)

        @app.post("/internal/outbox")
        def publish(authorization: str | None = Header(default=None)):
            configured = app.state.settings
            verify_service_identity(
                authorization, configured.scheduler_audience, configured.scheduler_service_account
            )
            return {"published": app.state.publisher.publish()}
    else:
        raise ValueError("APP_ROLE must be api or worker")
    return app


def run():
    import uvicorn

    uvicorn.run(
        create_app(role=os.getenv("APP_ROLE", "api")),
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8090")),
    )


if __name__ == "__main__":
    run()
