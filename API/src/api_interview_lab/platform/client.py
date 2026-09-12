"""One pooled client; bounded concurrency and retries only for GET requests."""
import asyncio
import random
from collections.abc import AsyncIterator
from datetime import UTC

import httpx


class PlatformClient:
    def __init__(self, base_url, *, auth=None, headers=None, concurrency=5, attempts=3,
                 transport=None):
        if concurrency < 1 or attempts < 1:
            raise ValueError('concurrency and attempts must be positive')
        combined = {'Accept': 'application/json', 'User-Agent': 'api-platform-lab/1.0'}
        combined.update(headers or {})
        self.client = httpx.AsyncClient(base_url=base_url, auth=auth, headers=combined, trust_env=False,
                                       timeout=httpx.Timeout(5, connect=2), transport=transport,
                                       limits=httpx.Limits(max_connections=concurrency))
        self.semaphore = asyncio.Semaphore(concurrency)
        self.attempts = attempts

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()

    async def get(self, path, params=None):
        async with self.semaphore:
            for attempt in range(self.attempts):
                delay = min(0.1 * 2 ** attempt + random.uniform(0, .1), 2)
                try:
                    response = await self.client.get(path, params=params)
                    if response.status_code not in {429, 502, 503, 504}:
                        response.raise_for_status()
                        return response.json()
                    if attempt == self.attempts - 1:
                        response.raise_for_status()
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            delay = float(retry_after)
                        except ValueError:
                            # HTTP-date values are valid too.
                            from datetime import datetime
                            from email.utils import parsedate_to_datetime
                            try:
                                delay = (parsedate_to_datetime(retry_after) -
                                         datetime.now(UTC)).total_seconds()
                            except (ValueError, TypeError, OverflowError):
                                delay = 1
                        if delay > 10:
                            response.raise_for_status()  # don't retry earlier than requested
                        delay = max(0, delay)
                except httpx.TransportError:
                    if attempt == self.attempts - 1:
                        raise
                await asyncio.sleep(delay)
        raise RuntimeError('Unreachable retry state')

    async def pages(self, service, limit=5) -> AsyncIterator[dict]:
        cursor = None
        seen = set()
        while True:
            params = {'limit': limit}
            if cursor:
                params['cursor'] = cursor
            page = await self.get(f'/{service}/api/v1/{service}', params)
            yield page
            cursor = page['next_cursor']
            if not cursor:
                return
            if cursor in seen:
                raise ValueError('Server repeated a pagination cursor')
            seen.add(cursor)

    async def summaries(self, services=('orders', 'customers', 'products')):
        async def fetch(service):
            try:
                count = 0
                async for page in self.pages(service):
                    count += len(page['items'])
                return {'service': service, 'count': count, 'error': None}
            except httpx.HTTPError as exc:
                return {'service': service, 'count': None, 'error': type(exc).__name__}
        tasks = [asyncio.create_task(fetch(s)) for s in services]
        try:
            for result in asyncio.as_completed(tasks):
                yield await result
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
