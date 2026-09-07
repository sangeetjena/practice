from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter

from api_interview_lab.config import get_settings
from api_interview_lab.server.graphql.schema import get_graphql_context, schema
from api_interview_lab.server.routers import health, orders

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="REST and GraphQL interview-reference API",
)
app.include_router(health.router)
app.include_router(orders.router, prefix="/api/v1")
app.include_router(GraphQLRouter(schema, context_getter=get_graphql_context), prefix="/graphql")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def run() -> None:
    uvicorn.run("api_interview_lab.server.main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
