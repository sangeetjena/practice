"""App factory shared by three separately deployed commerce services."""
import asyncio
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool

from .auth import Principal, require
from .config import Settings
from .store import Store, read_job, submit_job
from .telemetry import instrument


class Item(BaseModel):
    id: str
    name: str
    customer_id: str | None = None
    product_id: str | None = None
    quantity: int | None = None
    unit_price: float | None = None


class Page(BaseModel):
    items: list[Item]
    next_cursor: str | None


class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=120)
    customer_id: str = Field(pattern=r"^customers-[a-zA-Z0-9]+$", max_length=80)
    product_id: str = Field(pattern=r"^products-[a-zA-Z0-9]+$", max_length=80)
    quantity: int = Field(ge=1, le=10000)
    unit_price: float = Field(gt=0, le=1_000_000, allow_inf_nan=False)


class ImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    orders: list[OrderCreate] = Field(min_length=1, max_length=100)


def create_app(settings=None, store=None, transport=None):
    cfg = settings or Settings()
    cfg.validate()
    db = store or Store(cfg.database_url)

    @asynccontextmanager
    async def lifespan(app):
        yield
        await app.state.http.aclose()
        if hasattr(app.state, "tracer_provider"):
            app.state.tracer_provider.shutdown()
        if hasattr(app.state, "meter_provider"):
            app.state.meter_provider.shutdown()
        db.engine.dispose()

    app = FastAPI(title=f"Commerce {cfg.service} API", version="1.0.0",
                  description="Tenant-scoped interview lab. Supply one authentication method.",
                  lifespan=lifespan, root_path=cfg.root_path)
    app.state.settings = cfg
    app.state.store = db
    instrument(app, cfg.service, cfg.telemetry)
    app.state.http = httpx.AsyncClient(timeout=2, transport=transport, trust_env=False,
                                      limits=httpx.Limits(max_connections=10))
    if cfg.telemetry:
        HTTPXClientInstrumentor.instrument_client(
            app.state.http, tracer_provider=app.state.tracer_provider)

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return JSONResponse({"error": {"code": exc.status_code, "message": exc.detail},
                             "request_id": getattr(request.state, "request_id", None)},
                            status_code=exc.status_code, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # Do not reflect secret-bearing input values into errors/logs.
        return JSONResponse({"error": {"code": 422, "message": "Invalid request",
                                       "fields": [list(e["loc"]) for e in exc.errors()]}},
                            status_code=422)

    @app.exception_handler(Exception)
    async def unexpected(request, exc):
        return JSONResponse({"error": {"code": 500, "message": "Internal server error"},
                             "request_id": getattr(request.state, "request_id", None)},
                            status_code=500)

    @app.get("/health/live", tags=["operations"])
    def live():
        return {"status": "alive"}

    @app.get("/health/ready", tags=["operations"])
    def ready():
        try:
            db.ready()
        except SQLAlchemyError:
            raise HTTPException(503, "Database unavailable or schema missing") from None
        return {"status": "ready"}

    @app.get("/api/v1/catalog", tags=["catalog"], summary="Discover declared API contracts")
    def catalog(principal: Annotated[Principal, Depends(require("read"))]):
        return {"services": [{"name": name, "owner": "commerce-platform", "version": "v1",
                              "lifecycle": "experimental", "classification": "internal",
                              "docs": f"/{name}/docs", "spec": f"/{name}/openapi.json"}
                             for name in ("orders", "customers", "products")]}

    async def fault():
        if cfg.fault_delay_ms:
            await asyncio.sleep(min(cfg.fault_delay_ms, 10000) / 1000)
        if cfg.fault_fail:
            raise HTTPException(503, "Simulated service failure")

    path = f"/api/v1/{cfg.service}"

    @app.get(path, response_model=Page, tags=[cfg.service], summary="List tenant records",
             dependencies=[Depends(fault)])
    def listing(principal: Annotated[Principal, Depends(require("read"))],
                limit: int = Query(5, ge=1, le=100), cursor: str | None = Query(None, max_length=2048)):
        after = ""
        if cursor:
            try:
                decoded = jwt.decode(cursor, cfg.cursor_secret, algorithms=["HS256"],
                                     options={"require": ["tenant", "kind", "after"]})
                if decoded["tenant"] != principal.tenant or decoded["kind"] != cfg.service:
                    raise ValueError("Cursor context mismatch")
                after = decoded["after"]
                if not isinstance(after, str):
                    raise TypeError("Invalid key")
            except (jwt.PyJWTError, ValueError, TypeError):
                raise HTTPException(400, "Invalid pagination cursor") from None
        rows = db.page(principal.tenant, cfg.service, after, limit)
        more = len(rows) > limit
        rows = rows[:limit]
        next_cursor = jwt.encode({"tenant": principal.tenant, "kind": cfg.service,
                                  "after": rows[-1]["id"]}, cfg.cursor_secret,
                                 algorithm="HS256") if more else None
        return {"items": rows, "next_cursor": next_cursor}

    @app.get(path + "/{item_id}", response_model=Item, tags=[cfg.service],
             summary="Get a tenant record", dependencies=[Depends(fault)])
    def detail(item_id: str, principal: Annotated[Principal, Depends(require("read"))]):
        return db.get(principal.tenant, cfg.service, item_id)

    if cfg.service == "orders":
        @app.post("/api/v1/import-jobs", status_code=202, tags=["orders"],
                  summary="Durably enqueue a bounded sample order import")
        def submit(body: ImportRequest,
                   principal: Annotated[Principal, Depends(require("write"))],
                   idempotency_key: str = Header(min_length=1, max_length=128)):
            return submit_job(db, principal.tenant, idempotency_key,
                              [order.model_dump() for order in body.orders])

        @app.get("/api/v1/jobs/{job_id}", tags=["orders"], summary="Read tenant job state")
        def status(job_id: str, principal: Annotated[Principal, Depends(require("read"))]):
            return read_job(db, principal.tenant, job_id)

        @app.post(path, response_model=Item, status_code=201, tags=["orders"],
                  summary="Create an order idempotently")
        def create(body: OrderCreate, principal: Annotated[Principal, Depends(require("write"))],
                   idempotency_key: str = Header(min_length=1, max_length=128)):
            return db.create_order(principal.tenant, idempotency_key, body.model_dump())

        @app.get(path + "/{item_id}/customer", tags=["orders"],
                 summary="Resolve customer with a distributed trace")
        async def customer(item_id: str, request: Request,
                           principal: Annotated[Principal, Depends(require("read"))]):
            order = await run_in_threadpool(db.get, principal.tenant, "orders", item_id)
            headers = {h: request.headers[h] for h in ("authorization", "x-api-key")
                       if h in request.headers}
            client = app.state.http
            try:
                response = await client.get(
                    f"{cfg.customers_url}/api/v1/customers/{order['customer_id']}",
                    headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise HTTPException(504, "Customer service timed out") from None
            except (httpx.HTTPError, ValueError):
                raise HTTPException(502, "Customer service unavailable") from None
    return app
