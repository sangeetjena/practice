from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from api_interview_lab.domain.models import Order, OrderStatus
from api_interview_lab.patterns.source import OrderSource


class OrderPayload(BaseModel):
    """Validated transport model used at an untrusted API boundary."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    id: str = Field(min_length=1, examples=["ORD-1001"])
    customer_id: str = Field(min_length=1)
    product: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)
    status: OrderStatus = OrderStatus.CREATED

    @model_validator(mode="before")
    @classmethod
    def verify_and_remove_reported_revenue(cls, value: Any) -> Any:
        if not isinstance(value, dict) or "revenue" not in value:
            return value
        payload = value.copy()
        reported = float(payload.pop("revenue"))
        expected = round(float(payload["quantity"]) * float(payload["unit_price"]), 2)
        if reported != expected:
            raise ValueError("API revenue does not match quantity * unit_price")
        return payload

    @computed_field
    @property
    def revenue(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def to_domain(self) -> Order:
        return Order(**self.model_dump(exclude={"revenue"}))


class OrderPage(BaseModel):
    items: list[OrderPayload]
    page: int
    page_size: int
    total_items: int
    total_pages: int


def extract_with_pydantic(client: OrderSource) -> list[OrderPayload]:
    """Fetch API JSON and validate every untrusted item at the boundary."""
    return [OrderPayload.model_validate(item) for item in client.fetch_all_raw()]
