from __future__ import annotations

import asyncio
from pathlib import Path

from api_interview_lab.client.async_client import AsyncOrderClient
from api_interview_lab.patterns.dataclass_pattern import OrderRecord
from api_interview_lab.patterns.pandas_pattern import load_orders_frame, revenue_by_product
from api_interview_lab.patterns.pydantic_pattern import OrderPayload


async def demonstrate_asyncio() -> None:
    async with AsyncOrderClient("http://localhost:8000") as client:
        print("Pages in completion order:")
        async for page in client.stream_pages(page_size=3):
            print(f"  page={page.page}, items={len(page.items)}")


def main() -> None:
    raw = {"id": "ORD-X", "product": "Keyboard", "quantity": "2", "unit_price": "75"}
    print("Dataclass:", OrderRecord.from_dict(raw))

    validated = OrderPayload.model_validate(
        raw | {"customer_id": "CUS-X", "status": "created"}
    )
    print("Pydantic:", validated.model_dump())

    frame = load_orders_frame(Path("feeds/orders.csv"))
    print("pandas:\n", revenue_by_product(frame).head())
    asyncio.run(demonstrate_asyncio())


if __name__ == "__main__":
    main()

