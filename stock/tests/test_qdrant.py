import asyncio
import json
from datetime import datetime, timezone
from uuid import uuid4

import httpx

from stock_research.storage.qdrant import QdrantStore


def test_qdrant_upsert_and_search_use_observation_cutoff() -> None:
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET":
            return httpx.Response(404)
        if request.url.path.endswith("/points/query"):
            return httpx.Response(200, json={"result": {"points": []}})
        return httpx.Response(200, json={"result": True})

    async def scenario() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            store = QdrantStore("http://qdrant", "test-key", client=client)
            await store.ensure_collection(2)
            cutoff = datetime(2026, 9, 30, tzinfo=timezone.utc)
            await store.upsert_evidence(
                uuid4(), [0.1, 0.2], symbol="IBM", observed_at=cutoff,
                source="news", text_hash="sha256:test",
            )
            assert await store.search([0.1, 0.2], symbol="IBM", cutoff_at=cutoff) == []
            assert all(request.headers["api-key"] == "test-key" for request in requests)
            query = json.loads(requests[-1].content)
            assert query["filter"]["must"][1]["range"]["lte"] == cutoff.isoformat()

    asyncio.run(scenario())
