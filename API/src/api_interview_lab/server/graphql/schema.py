from __future__ import annotations

from typing import Annotated

import strawberry
from fastapi import Depends
from strawberry.types import Info

from api_interview_lab.data.repository import OrderRepository
from api_interview_lab.domain.models import Order
from api_interview_lab.server.dependencies import get_repository


def get_graphql_context(
    repository: Annotated[OrderRepository, Depends(get_repository)],
) -> dict[str, OrderRepository]:
    return {"repository": repository}


@strawberry.type
class OrderType:
    id: str
    customer_id: str
    product: str
    quantity: int
    unit_price: float
    status: str

    @strawberry.field
    def revenue(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    @classmethod
    def from_domain(cls, order: Order) -> OrderType:
        return cls(
            id=order.id,
            customer_id=order.customer_id,
            product=order.product,
            quantity=order.quantity,
            unit_price=order.unit_price,
            status=order.status.value,
        )


@strawberry.type
class Query:
    @strawberry.field
    def order(self, info: Info, order_id: str) -> OrderType | None:
        order = info.context["repository"].get(order_id)
        return OrderType.from_domain(order) if order else None

    @strawberry.field
    def orders(self, info: Info, limit: int = 10, offset: int = 0) -> list[OrderType]:
        rows, _ = info.context["repository"].list(
            offset=max(offset, 0), limit=min(max(limit, 1), 100)
        )
        return [OrderType.from_domain(order) for order in rows]


schema = strawberry.Schema(query=Query)
