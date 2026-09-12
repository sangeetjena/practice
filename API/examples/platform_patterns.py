"""Fetch live APIs, then represent responses as JSON, Pydantic, dataclasses or pandas."""
import asyncio
import os
from dataclasses import dataclass

import pandas as pd

from api_interview_lab.platform.app import Item
from api_interview_lab.platform.client import PlatformClient


@dataclass
class OrderRecord:
    id: str
    name: str
    quantity: int


async def main():
    async with PlatformClient('http://localhost:8080',
                              headers={'X-API-Key': os.environ['DEMO_API_KEY']}) as client:
        raw = []
        async for page in client.pages('orders'):
            raw.extend(page['items'])
        validated = [Item.model_validate(row) for row in raw]
        records = [OrderRecord(row.id, row.name, row.quantity) for row in validated]
        print(records[:2])
        print(pd.DataFrame(raw)[['id', 'quantity']].head())
        async for result in client.summaries():
            print(result)  # results arrive as each service finishes


if __name__ == '__main__':
    asyncio.run(main())
