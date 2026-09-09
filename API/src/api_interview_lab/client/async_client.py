from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Mapping
from typing import Any, Self

import httpx

from api_interview_lab.client.auth import AuthStrategy
from api_interview_lab.client.base import build_headers, expect_object
from api_interview_lab.patterns.pydantic_pattern import OrderPage, OrderPayload


class AsyncOrderClient:
    def __init__(
        self,
        base_url: str,
        *,
        auth: AuthStrategy | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = 10.0,
        concurrency: int = 5,
        transport: httpx.AsyncBaseTransport | None = None,
        trust_env: bool = True,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=build_headers(headers, auth),
            timeout=httpx.Timeout(timeout),
            transport=transport,
            trust_env=trust_env,
        )
        self._semaphore = asyncio.Semaphore(concurrency)

    async def _get_page_raw(self, page: int, page_size: int) -> dict[str, Any]:
        async with self._semaphore:
            response = await self._client.get(
                "/api/v1/orders", params={"page": page, "page_size": page_size}
            )
            response.raise_for_status()
            return expect_object(response.json())

    async def _get_page(self, page: int, page_size: int) -> OrderPage:
        return OrderPage.model_validate(await self._get_page_raw(page, page_size))

    async def fetch_all_raw(self, page_size: int = 5) -> list[dict[str, Any]]:
        first = await self._get_page_raw(1, page_size)
        tasks = [
            self._get_page_raw(page, page_size)
            for page in range(2, int(first["total_pages"]) + 1)
        ]
        remaining = await asyncio.gather(*tasks)
        return list(first["items"]) + [item for page in remaining for item in page["items"]]

    async def fetch_all_ordered(self, page_size: int = 5) -> list[OrderPayload]:
        """gather preserves input order and raises on the first propagated failure."""
        first = await self._get_page(1, page_size)
        tasks = [self._get_page(page, page_size) for page in range(2, first.total_pages + 1)]
        remaining = await asyncio.gather(*tasks)
        return first.items + [item for page in remaining for item in page.items]

    async def stream_pages(self, page_size: int = 5) -> AsyncIterator[OrderPage]:
        """Yield page 1, then remaining pages in completion order."""
        first = await self._get_page(1, page_size)
        yield first
        tasks = [
            asyncio.create_task(self._get_page(page, page_size))
            for page in range(2, first.total_pages + 1)
        ]
        try:
            for task in asyncio.as_completed(tasks):
                yield await task
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
