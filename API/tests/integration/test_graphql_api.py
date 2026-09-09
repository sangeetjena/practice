from fastapi.testclient import TestClient

from api_interview_lab.config import Settings, get_settings
from api_interview_lab.server.main import app


def test_graphql_orders(client: TestClient) -> None:
    response = client.post(
        "/graphql",
        json={"query": "{ orders(limit: 2) { id product revenue status } }"},
    )
    assert response.status_code == 200
    assert len(response.json()["data"]["orders"]) == 2


def test_graphql_requires_bearer_token_when_configured(client: TestClient) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(api_token="secret")
    try:
        response = client.post("/graphql", json={"query": "{ orders { id } }"})
        assert response.status_code == 401
    finally:
        app.dependency_overrides.pop(get_settings, None)
