from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_items_empty():
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_item():
    payload = {"name": "Widget", "price": 9.99}
    response = client.post("/api/v1/items/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Widget"
    assert data["price"] == 9.99
    assert data["id"] == 1


def test_get_item():
    response = client.get("/api/v1/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"


def test_update_item():
    response = client.put("/api/v1/items/1", json={"price": 14.99})
    assert response.status_code == 200
    assert response.json()["price"] == 14.99


def test_delete_item():
    response = client.delete("/api/v1/items/1")
    assert response.status_code == 204


def test_get_item_not_found():
    response = client.get("/api/v1/items/999")
    assert response.status_code == 404
