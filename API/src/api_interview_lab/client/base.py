from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api_interview_lab.client.auth import AuthStrategy

DEFAULT_HEADERS: dict[str, str] = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "api-interview-lab-client/1.0",
}


def build_headers(
    headers: Mapping[str, str] | None = None,
    auth: AuthStrategy | None = None,
) -> dict[str, str]:
    """Merge defaults, caller overrides, and auth (highest precedence)."""
    merged = {**DEFAULT_HEADERS, **(headers or {})}
    if auth is not None:
        merged.update(auth.headers())
    return merged


def expect_object(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TypeError("Expected the API to return a JSON object")
    return payload
