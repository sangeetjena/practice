from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api_interview_lab.data.repository import OrderRepository
from api_interview_lab.server.dependencies import get_repository

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/ready")
def readiness(
    repository: Annotated[OrderRepository, Depends(get_repository)],
) -> dict[str, str]:
    if not repository.healthcheck():
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ready"}
