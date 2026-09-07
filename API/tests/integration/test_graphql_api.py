from fastapi.testclient import TestClient


def test_graphql_orders(client: TestClient) -> None:
    response = client.post(
        "/graphql",
        json={"query": "{ orders(limit: 2) { id product revenue status } }"},
    )
    assert response.status_code == 200
    assert len(response.json()["data"]["orders"]) == 2

