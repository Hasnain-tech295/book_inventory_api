import pytest
from fastapi.testclient import TestClient
from main import app, books_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    original = books_db.copy()
    yield
    books_db.clear()
    books_db.update(original)


# ---------------------------------------------------------------
# Error shape contract tests
# These test that your API always returns the same error format.
# If these break, every client that calls your API breaks.
# ---------------------------------------------------------------

def test_404_has_correct_error_shape():
    response = client.get("/books/9999")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "BOOK_NOT_FOUND"
    assert "message" in body
    assert "request_id" in body
    assert "9999" in body["message"]

def test_422_has_correct_error_shape():
    response = client.post("/books", json={"title": "", "author": "X", "year": -1})
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "details" in body
    assert isinstance(body["details"], list)
    # Each detail must have field, message, type
    for detail in body["details"]:
        assert "field" in detail
        assert "message" in detail

def test_409_on_duplicate_isbn():
    # Create book with ISBN
    client.post("/books", json={
        "title": "Original", "author": "A", "year": 2000, "isbn": "9780061120084"
    })
    # Try to create another with same ISBN
    response = client.post("/books", json={
        "title": "Duplicate", "author": "B", "year": 2001, "isbn": "9780061120084"
    })
    assert response.status_code == 409
    body = response.json()
    assert body["error"] == "DUPLICATE_ISBN"
    assert "request_id" in body

def test_500_returns_safe_message():
    # The /debug/crash route triggers an unhandled RuntimeError
    response = client.get("/debug/crash")
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "INTERNAL_ERROR"
    # Critical: stack trace must NOT be in the response
    assert "RuntimeError" not in str(body)
    assert "Traceback" not in str(body)
    assert "request_id" in body

def test_response_headers_present():
    response = client.get("/books/1")
    assert "x-request-id" in response.headers
    assert "x-process-time" in response.headers

def test_each_request_gets_unique_request_id():
    r1 = client.get("/books/1")
    r2 = client.get("/books/1")
    assert r1.headers["x-request-id"] != r2.headers["x-request-id"]

def test_delete_nonexistent_book_error_shape():
    response = client.delete("/books/9999")
    assert response.status_code == 404
    assert response.json()["error"] == "BOOK_NOT_FOUND"