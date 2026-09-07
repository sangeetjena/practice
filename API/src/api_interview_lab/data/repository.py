from __future__ import annotations

from typing import Protocol

from api_interview_lab.domain.models import Order


class OrderRepository(Protocol):
    def list(self, *, offset: int, limit: int) -> tuple[list[Order], int]: ...

    def get(self, order_id: str) -> Order | None: ...

    def create(self, order: Order) -> Order: ...

    def healthcheck(self) -> bool: ...

