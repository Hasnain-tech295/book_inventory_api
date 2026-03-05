from fastapi.testclient import TestClient
from book_api import app

client = TestClient(app)

def test_list_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_book():
    response = client.get("/books/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "The Great Gatsby"
    assert data["author"] == "F. Scott Fitzgerald"
    assert data["year"] == 1925
    assert data["price"] == 10.99

def test_get_book_not_found():
    response = client.get("/books/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"

def test_create_book():
    response = client.post("/books", json={
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "year": 1925,
        "price": 10.99
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "The Great Gatsby"
    assert data["author"] == "F. Scott Fitzgerald"
    assert data["year"] == 1925
    assert data["price"] == 10.99

def test_delete_book():
    response = client.delete("/books/1")
    assert response.status_code == 204

def test_delete_book_not_found():
    response = client.delete("/books/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"