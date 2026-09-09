from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from api_interview_lab.domain.models import OrderStatus
from api_interview_lab.patterns.source import OrderSource


@dataclass(frozen=True, slots=True)
class OrderRecord:
    id: str
    customer_id: str
    product: str
    quantity: int
    unit_price: float
    status: OrderStatus

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> OrderRecord:
        """Explicit conversion: fast and dependency-free, but validation is manual."""
        return cls(
            id=str(payload["id"]),
            customer_id=str(payload["customer_id"]),
            product=str(payload["product"]),
            quantity=int(payload["quantity"]),
            unit_price=float(payload["unit_price"]),
            status=OrderStatus(payload["status"]),
        )

    @property
    def revenue(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def extract_with_dataclasses(client: OrderSource) -> list[OrderRecord]:
    """Fetch API JSON and explicitly convert it to dependency-free records."""
    return [OrderRecord.from_dict(item) for item in client.fetch_all_raw()]
