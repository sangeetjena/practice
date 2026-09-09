from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self

import httpx

from api_interview_lab.client.auth import AuthStrategy
from api_interview_lab.client.base import build_headers, expect_object
from api_interview_lab.patterns.pydantic_pattern import OrderPage, OrderPayload


class SyncOrderClient:
    def __init__(
        self,
        base_url: str,
        *,
        auth: AuthStrategy | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
        trust_env: bool = True,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers=build_headers(headers, auth),
            timeout=httpx.Timeout(timeout),
            transport=transport,
            trust_env=trust_env,
        )

    def get_order_raw(self, order_id: str) -> dict[str, Any]:
        response = self._client.get(f"/api/v1/orders/{order_id}")
        response.raise_for_status()
        return expect_object(response.json())

    def get_order(self, order_id: str) -> OrderPayload:
        return OrderPayload.model_validate(self.get_order_raw(order_id))

    def list_orders_raw(self, page: int = 1, page_size: int = 10) -> dict[str, Any]:
        response = self._client.get(
            "/api/v1/orders", params={"page": page, "page_size": page_size}
        )
        response.raise_for_status()
        return expect_object(response.json())

    def list_orders(self, page: int = 1, page_size: int = 10) -> OrderPage:
        return OrderPage.model_validate(self.list_orders_raw(page, page_size))

    def fetch_all_raw(self, page_size: int = 100) -> list[dict[str, Any]]:
        first = self.list_orders_raw(page=1, page_size=page_size)
        items = list(first["items"])
        for page in range(2, int(first["total_pages"]) + 1):
            items.extend(self.list_orders_raw(page=page, page_size=page_size)["items"])
        return items

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
