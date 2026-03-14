from fastapi.testclient import TestClient
from main import app, books_db, next_id
import pytest

client = TestClient(app)

# --- Helper: reset state before each test so tests don't affect each other --
@pytest.fixture(autouse=True)
def reset_db():
    # Save original state
    original_db = books_db.copy()
    yield

    # Restore after each test
    books_db.clear()
    books_db.update(original_db)

# ---------------------------------------------------------------
# List / Filter tests
# ---------------------------------------------------------------
def test_list_all_books():
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4   # our seed data

def test_filter_by_author():
    response = client.get("/books?author=tolkien")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "The Hobbit"

def test_filter_by_year_range():
    response = client.get("/books?min_year=1960&max_year=1980")
    assert response.status_code == 200
    data = response.json()
    # Dune (1965) and Neuromancer (1984 — outside range) and Le Guin (1969)
    years = [b["year"] for b in data]
    assert all(1960 <= y <= 1980 for y in years)

def test_pagination():
    response = client.get("/books?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    response2 = client.get("/books?limit=2&offset=2")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2) == 2

    # Offset beyond results -> empty list, not error
    response3 = client.get("/books?limit=10&offset=999")
    assert response3.status_code == 200
    assert response3.json() == []

# ---------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------
def test_create_book_invalid_year_returns_422():
    response = client.post("/books", json={"title": "X", "author": "Y", "year": -1})
    assert response.status_code == 422

def test_create_book_empty_title_returns_422():
    response = client.post("/books", json={"title": "", "author": "Y", "year": 2000})
    assert response.status_code == 422

def test_create_book_missing_required_field_returns_422():
    # Missing 'year'
    response = client.post("/books", json={"title": "X", "author": "Y"})
    assert response.status_code == 422

def test_create_book_invalid_isbn_returns_422():
    response = client.post("/books", json={
        "title": "X", "author": "Y", "year": 2000, "isbn": "not-an-isbn"
    })
    assert response.status_code == 422

def test_create_book_valid_isbn_normalizes():
    response = client.post("/books", json={
        "title": "X", "author": "Y", "year": 2000, "isbn": "978-0-06-112008-4"
    })
    assert response.status_code == 201
    # Hyphens stripped by validator
    assert response.json()["isbn"] == "9780061120084"


# ---------------------------------------------------------------
# PATCH tests
# ---------------------------------------------------------------
def test_patch_updates_only_sent_fields():
    original = client.get("/books/1").json()
    response = client.patch("/books/1", json={"title": "New Title"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "New Title"
    # author and year must be unchanged
    assert updated["author"] == original["author"]
    assert updated["year"] == original["year"]

def test_patch_nonexistent_book_returns_404():
    response = client.patch("/books/9999", json={"title": "X"})
    assert response.status_code == 404

# ---------------------------------------------------------------
# Limit/offset validation
# ---------------------------------------------------------------
def test_limit_above_max_returns_422():
    response = client.get("/books?limit=9999")
    assert response.status_code == 422

def test_negative_offset_returns_422():
    response = client.get("/books?offset=-1")
    assert response.status_code == 422