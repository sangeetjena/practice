from fastapi.testclient import TestClient


def test_list_orders(client: TestClient) -> None:
    response = client.get("/api/v1/orders", params={"page": 2, "page_size": 2})
    assert response.status_code == 200
    assert response.json()["total_pages"] == 3
    assert len(response.json()["items"]) == 2


def test_get_missing_order(client: TestClient) -> None:
    response = client.get("/api/v1/orders/not-found")
    assert response.status_code == 404


def test_create_order(client: TestClient) -> None:
    response = client.post(
        "/api/v1/orders",
        json={
            "id": "ORD-NEW", "customer_id": "CUS-2", "product": "Monitor",
            "quantity": 1, "unit_price": 300, "status": "created",
        },
    )
    assert response.status_code == 201
    assert response.json()["revenue"] == 300

