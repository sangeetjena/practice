from __future__ import annotations

import httpx

from api_interview_lab.client import DEFAULT_HEADERS, BearerTokenAuth, SyncOrderClient


def test_client_sends_default_custom_and_auth_headers() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Accept"] == DEFAULT_HEADERS["Accept"]
        assert request.headers["User-Agent"] == "interview-test"
        assert request.headers["Authorization"] == "Bearer secret"
        return httpx.Response(
            200,
            json={
                "items": [], "page": 1, "page_size": 10,
                "total_items": 0, "total_pages": 0,
            },
        )

    with SyncOrderClient(
        "https://example.test",
        auth=BearerTokenAuth("secret"),
        headers={"User-Agent": "interview-test"},
        transport=httpx.MockTransport(handler),
    ) as client:
        assert client.list_orders().items == []


def test_fetch_all_raw_walks_pagination() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params["page"])
        return httpx.Response(
            200,
            json={
                "items": [{"id": str(page)}], "page": page, "page_size": 1,
                "total_items": 2, "total_pages": 2,
            },
        )

    with SyncOrderClient(
        "https://example.test", transport=httpx.MockTransport(handler)
    ) as client:
        assert client.fetch_all_raw(page_size=1) == [{"id": "1"}, {"id": "2"}]
