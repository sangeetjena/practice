from __future__ import annotations

from typing import Any, Protocol


class OrderSource(Protocol):
    """Small client contract that keeps extraction patterns easy to test."""

    def fetch_all_raw(self, page_size: int = 100) -> list[dict[str, Any]]: ...
