from __future__ import annotations

from typing import Any, TypedDict, cast

from api_interview_lab.patterns.source import OrderSource


class OrderDict(TypedDict):
    id: str
    customer_id: str
    product: str
    quantity: int
    unit_price: float
    status: str
    revenue: float


def extract_with_typed_dict(client: OrderSource) -> list[OrderDict]:
    """Add static type hints to API dictionaries without runtime validation."""
    items: list[dict[str, Any]] = client.fetch_all_raw()
    return cast(list[OrderDict], items)
