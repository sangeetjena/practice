from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, computed_field

from api_interview_lab.domain.models import Order, OrderStatus


class OrderPayload(BaseModel):
    """Validated transport model used at an untrusted API boundary."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    id: str = Field(min_length=1, examples=["ORD-1001"])
    customer_id: str = Field(min_length=1)
    product: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)
    status: OrderStatus = OrderStatus.CREATED

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

