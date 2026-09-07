from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from api_interview_lab.data.sqlite_repository import SQLiteOrderRepository
from api_interview_lab.patterns.pydantic_pattern import OrderPayload
from api_interview_lab.server.dependencies import get_repository
from api_interview_lab.server.main import app


@pytest.fixture
def repository(tmp_path) -> SQLiteOrderRepository:
    repo = SQLiteOrderRepository(tmp_path / "test.db")
    for index in range(1, 7):
        repo.create(
            OrderPayload(
                id=f"ORD-{index}", customer_id="CUS-1", product="Keyboard",
                quantity=index, unit_price=10.0, status="paid",
            ).to_domain()
        )
    return repo


@pytest.fixture
def client(repository: SQLiteOrderRepository) -> Iterator[TestClient]:
    app.dependency_overrides[get_repository] = lambda: repository
    get_repository.cache_clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

