from __future__ import annotations

from typing import Self

import httpx

from api_interview_lab.patterns.pydantic_pattern import OrderPage, OrderPayload


class SyncOrderClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def get_order(self, order_id: str) -> OrderPayload:
        response = self._client.get(f"/api/v1/orders/{order_id}")
        response.raise_for_status()
        return OrderPayload.model_validate(response.json())

    def list_orders(self, page: int = 1, page_size: int = 10) -> OrderPage:
        response = self._client.get(
            "/api/v1/orders", params={"page": page, "page_size": page_size}
        )
        response.raise_for_status()
        return OrderPage.model_validate(response.json())

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
