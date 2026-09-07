from __future__ import annotations

import math
import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api_interview_lab.data.repository import OrderRepository
from api_interview_lab.patterns.pydantic_pattern import OrderPage, OrderPayload
from api_interview_lab.server.dependencies import get_repository

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=OrderPage)
def list_orders(
    repository: Annotated[OrderRepository, Depends(get_repository)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> OrderPage:
    orders, total = repository.list(offset=(page - 1) * page_size, limit=page_size)
    return OrderPage(
        items=[OrderPayload.model_validate(order, from_attributes=True) for order in orders],
        page=page,
        page_size=page_size,
        total_items=total,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{order_id}", response_model=OrderPayload)
def get_order(
    order_id: str,
    repository: Annotated[OrderRepository, Depends(get_repository)],
) -> OrderPayload:
    order = repository.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderPayload.model_validate(order, from_attributes=True)


@router.post("", response_model=OrderPayload, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderPayload,
    repository: Annotated[OrderRepository, Depends(get_repository)],
) -> OrderPayload:
    try:
        return OrderPayload.model_validate(
            repository.create(payload.to_domain()), from_attributes=True
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Order already exists") from exc
