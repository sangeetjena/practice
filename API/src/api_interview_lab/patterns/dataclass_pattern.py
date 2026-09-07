from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class OrderRecord:
    id: str
    product: str
    quantity: int
    unit_price: float

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> OrderRecord:
        """Explicit conversion: fast and dependency-free, but validation is manual."""
        return cls(
            id=str(payload["id"]),
            product=str(payload["product"]),
            quantity=int(payload["quantity"]),
            unit_price=float(payload["unit_price"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

