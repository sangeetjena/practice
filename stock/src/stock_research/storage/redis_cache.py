"""Ephemeral cache and cooldowns; Redis is never a decision source of truth."""

import json
from typing import Any

from redis.asyncio import Redis


class RedisCache:
    def __init__(self, client: Redis) -> None:
        self.client = client

    @classmethod
    def connect(cls, url: str) -> "RedisCache":
        if not url:
            raise ValueError("STOCK_REDIS_URL is required")
        return cls(Redis.from_url(url, decode_responses=True))

    async def close(self) -> None:
        await self.client.aclose()

    async def put(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be positive")
        await self.client.set(key, json.dumps(value), ex=ttl_seconds)

    async def get(self, key: str) -> dict[str, Any] | None:
        raw = await self.client.get(key)
        return json.loads(raw) if raw is not None else None

    async def claim_cooldown(self, key: str, ttl_seconds: int) -> bool:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be positive")
        return bool(await self.client.set(key, "1", ex=ttl_seconds, nx=True))
