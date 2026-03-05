from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_users_returns_200():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_existing_user():
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Ada Lovelace"
    assert data["email"] == "ada@example.com"

def test_get_nonexistent_user_returns_404():
    response = client.get("/users/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_create_user():
    payload = {"name": "Grace Hopper", "email": "grace@example.com"}
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Grace Hopper"
    assert "id" in data

def test_delete_user():
    response = client.delete("/users/2")
    assert response.status_code == 204

def test_delete_nonexistent_user_returns_404():
    response = client.delete("/users/9999")
    assert response.status_code == 404