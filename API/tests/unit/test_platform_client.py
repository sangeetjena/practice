import asyncio

import httpx
import pytest

from api_interview_lab.platform.client import PlatformClient


@pytest.mark.asyncio
async def test_retry_and_auth_failure():
    calls = []
    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(429, headers={'Retry-After': '0'})
        return httpx.Response(200, json={'ok': True})
    async with PlatformClient('http://test', transport=httpx.MockTransport(handler)) as client:
        assert await client.get('/test') == {'ok': True}
        assert len(calls) == 2
    calls.clear()
    def unauthorized(request):
        calls.append(request)
        return httpx.Response(401)
    async with PlatformClient('http://test', transport=httpx.MockTransport(unauthorized)) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.get('/test')
        assert len(calls) == 1


@pytest.mark.asyncio
async def test_pagination_and_completion_order():
    async def handler(request):
        service = request.url.path.split('/')[1]
        if service == 'orders':
            await asyncio.sleep(.02)
        return httpx.Response(200, json={'items': [{'id': service}], 'next_cursor': None})
    async with PlatformClient('http://test', transport=httpx.MockTransport(handler)) as client:
        results = [result async for result in client.summaries()]
        assert results[-1]['service'] == 'orders'
        assert all(r['count'] == 1 for r in results)


@pytest.mark.asyncio
async def test_repeated_cursor_and_cancellation():
    def handler(request):
        return httpx.Response(200, json={'items': [], 'next_cursor': 'same'})
    async with PlatformClient('http://test', transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError, match='repeated'):
            _ = [page async for page in client.pages('orders')]
    finished = asyncio.Event()
    async def slow(request):
        try:
            await asyncio.sleep(10)
        finally:
            finished.set()
    async with PlatformClient('http://test', transport=httpx.MockTransport(slow)) as client:
        task = asyncio.create_task(client.get('/test'))
        await asyncio.sleep(.01)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert finished.is_set()
