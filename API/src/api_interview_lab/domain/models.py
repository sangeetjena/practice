from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OrderStatus(StrEnum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Order:
    id: str
    customer_id: str
    product: str
    quantity: int
    unit_price: float
    status: OrderStatus

    @property
    def revenue(self) -> float:
        return round(self.quantity * self.unit_price, 2)

