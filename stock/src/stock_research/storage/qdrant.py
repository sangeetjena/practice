"""Semantic evidence storage backed by the existing INFRA Qdrant service."""

from datetime import datetime
from typing import Any
from uuid import UUID

import httpx

from stock_research.domain.models import require_aware


class QdrantStore:
    def __init__(
        self, url: str, api_key: str, *, collection: str = "stock_evidence",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not url or not api_key:
            raise ValueError("Qdrant URL and API key are required")
        self.url = url.rstrip("/")
        self.collection = collection
        self.client = client or httpx.AsyncClient(timeout=20.0)
        self._owns_client = client is None
        self.headers = {"api-key": api_key}

    async def aclose(self) -> None:
        if self._owns_client:
            await self.client.aclose()

    async def ensure_collection(self, dimensions: int) -> None:
        if dimensions < 1:
            raise ValueError("dimensions must be positive")
        url = f"{self.url}/collections/{self.collection}"
        response = await self.client.get(url, headers=self.headers)
        if response.status_code == 404:
            response = await self.client.put(
                url, headers=self.headers,
                json={
                    "vectors": {"size": dimensions, "distance": "Cosine"},
                    "shard_number": 3, "replication_factor": 2,
                    "write_consistency_factor": 1,
                },
            )
        response.raise_for_status()
        for field, schema in (("symbol", "keyword"), ("observed_at", "datetime")):
            index_response = await self.client.put(
                f"{url}/index", headers=self.headers,
                json={"field_name": field, "field_schema": schema},
            )
            index_response.raise_for_status()

    async def upsert_evidence(
        self, evidence_id: UUID, vector: list[float], *, symbol: str,
        observed_at: datetime, source: str, text_hash: str,
    ) -> None:
        require_aware(observed_at)
        if not vector:
            raise ValueError("vector cannot be empty")
        response = await self.client.put(
            f"{self.url}/collections/{self.collection}/points?wait=true",
            headers=self.headers,
            json={"points": [{
                "id": str(evidence_id), "vector": vector,
                "payload": {
                    "symbol": symbol, "observed_at": observed_at.isoformat(),
                    "source": source, "text_hash": text_hash,
                },
            }]},
        )
        response.raise_for_status()

    async def search(
        self, vector: list[float], *, symbol: str, cutoff_at: datetime, limit: int = 10
    ) -> list[dict[str, Any]]:
        require_aware(cutoff_at)
        if not vector or limit < 1:
            raise ValueError("vector and positive limit are required")
        response = await self.client.post(
            f"{self.url}/collections/{self.collection}/points/query",
            headers=self.headers,
            json={
                "query": vector, "limit": limit, "with_payload": True,
                "filter": {"must": [
                    {"key": "symbol", "match": {"value": symbol}},
                    {"key": "observed_at", "range": {"lte": cutoff_at.isoformat()}},
                ]},
            },
        )
        response.raise_for_status()
        return list(response.json()["result"]["points"])
