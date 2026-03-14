from fastapi.testclient import TestClient
from book_inventory import app

client = TestClient(app)

def test_get_all_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_existing_book():
    response = client.get("/books/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925, "price": 10.99}

def test_get_nonexistent_book():
    response = client.get("/books/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}

def test_create_book():
    payload = {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925, "price": 10.99}
    response = client.post("/books", json=payload)
    assert response.status_code == 201
    assert response.json() == {"id": 6, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925, "price": 10.99}

def test_delete_book():
    response = client.delete("/books/1")
    assert response.status_code == 204

def test_delete_nonexistent_book():
    response = client.delete("/books/999")
    assert response.status_code == 404
    