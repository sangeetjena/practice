from __future__ import annotations

import asyncio
import os

from api_interview_lab.client import BearerTokenAuth, SyncOrderClient
from api_interview_lab.client.async_client import AsyncOrderClient
from api_interview_lab.patterns import (
    extract_with_dataclasses,
    extract_with_pandas,
    extract_with_pydantic,
    extract_with_typed_dict,
)
from api_interview_lab.patterns.pandas_pattern import revenue_by_product

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TOKEN = os.getenv("API_TOKEN")


def auth() -> BearerTokenAuth | None:
    return BearerTokenAuth(TOKEN) if TOKEN else None


async def demonstrate_asyncio() -> None:
    async with AsyncOrderClient(BASE_URL, auth=auth(), trust_env=False) as client:
        print("Pages in completion order:")
        async for page in client.stream_pages(page_size=3):
            print(f"  page={page.page}, items={len(page.items)}")


def main() -> None:
    with SyncOrderClient(BASE_URL, auth=auth(), trust_env=False) as client:
        print("TypedDict:", extract_with_typed_dict(client)[:1])
        print("Dataclass:", extract_with_dataclasses(client)[:1])
        print("Pydantic:", extract_with_pydantic(client)[:1])
        frame = extract_with_pandas(client)
        print("pandas aggregation:\n", revenue_by_product(frame).head())
    asyncio.run(demonstrate_asyncio())


if __name__ == "__main__":
    main()
