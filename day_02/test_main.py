import pytest
from fastapi.testclient import TestClient
from main import app, books_db

client = TestClient(app)

# Helper: reset state before each test so tests don't affect each other
@pytest.fixture(autouse=True)
def reset_db():
    original_db = books_db.copy()
    yield
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
    assert len(data) == 10


def test_filter_books_by_author():
    response = client.get("/books?author=Douglas Adams")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["author"] == "Douglas Adams"
    assert data[0]["title"] == "The Hitchhiker's Guide to the Galaxy"
    assert data[0]["year"] == 1979

def test_filter_books_by_year():
    response = client.get("/books?min_year=1979&max_year=2000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    years = [item["year"] for item in data]
    assert all(year >= 1979 and year <= 2000 for year in years)

def test_pagination():
    response = client.get("/books?limit=2&offset=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 3
    assert data[1]["id"] == 4

# ---------------------------------------------------------------
# Get /books/{book_id}
# ---------------------------------------------------------------
def test_get_book_by_id():
    response = client.get("/books/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "The Hitchhiker's Guide to the Galaxy"
    assert data["author"] == "Douglas Adams"
    assert data["year"] == 1979

# ---------------------------------------------------------------
# Post /books
# ---------------------------------------------------------------
def test_create_book():
    response = client.post("/books", json={
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "year": 1979,
        "isbn": "9780345391803"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 21
    assert data["title"] == "The Hitchhiker's Guide to the Galaxy"
    assert data["author"] == "Douglas Adams"
    assert data["year"] == 1979

# ---------------------------------------------------------------
# Patch /books/{book_id}
# ---------------------------------------------------------------
def test_update_book():
    response = client.patch("/books/1", json={
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "year": 1979,
        "isbn": "9780345391803"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "The Hitchhiker's Guide to the Galaxy"
    assert data["author"] == "Douglas Adams"
    assert data["year"] == 1979
    assert data["isbn"] == "9780345391803"

def test_update_nonexisting_book():
    response = client.patch("/books/100", json={
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "year": 1979,
        "isbn": "9780345391803"
    })
    assert response.status_code == 404