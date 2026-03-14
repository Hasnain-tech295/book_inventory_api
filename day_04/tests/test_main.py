import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..dependencies import (
    get_db, get_current_user, require_admin,
    FakeDB, CurrentUser, _books_store,
)


# ---------------------------------------------------------------
# Test DB — isolated store per test run
# ---------------------------------------------------------------
TEST_BOOKS: dict[int, dict] = {
    1: {"id": 1, "title": "The Hobbit",   "author": "Tolkien", "year": 1937, "isbn": None},
    2: {"id": 2, "title": "Dune",          "author": "Herbert", "year": 1965, "isbn": None},
}

def get_test_db():
    """Override: inject a fresh test DB instead of the real one."""
    db = FakeDB(TEST_BOOKS.copy())
    try:
        yield db
    finally:
        db.close()

# Fake users for testing
FAKE_ADMIN  = CurrentUser(user_id=99, name="Test Admin",  role="admin")
FAKE_READER = CurrentUser(user_id=98, name="Test Reader", role="reader")

def get_admin_user():
    return FAKE_ADMIN

def get_reader_user():
    return FAKE_READER


# ---------------------------------------------------------------
# Fixtures: build clients with different auth contexts
# This is the power of dependency injection in tests.
# ---------------------------------------------------------------

@pytest.fixture
def public_client():
    """Client with DB override but no auth."""
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def admin_client():
    """Client authenticated as admin."""
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_current_user] = get_admin_user
    app.dependency_overrides[require_admin] = get_admin_user
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def reader_client():
    """Client authenticated as reader (non-admin)."""
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_current_user] = get_reader_user
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------
# Tests
# ---------------------------------------------------------------

def test_list_books_public(public_client):
    response = public_client.get("/books")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_pagination(public_client):
    response = public_client.get("/books?limit=1&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_filter_by_author(public_client):
    response = public_client.get("/books?author=tolkien")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "The Hobbit"

# --- Auth tests ---

def test_create_book_requires_auth(public_client):
    """No auth override → real get_current_user runs → 401."""
    response = public_client.post(
        "/books",
        json={"title": "X", "author": "Y", "year": 2000}
    )
    assert response.status_code == 401

def test_create_book_as_reader(reader_client):
    response = reader_client.post(
        "/books",
        json={"title": "Foundation", "author": "Asimov", "year": 1951}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Foundation"

def test_delete_book_as_admin(admin_client):
    response = admin_client.delete("/books/1")
    assert response.status_code == 204

def test_delete_book_as_reader_returns_403(reader_client):
    """
    Reader client does NOT override require_admin,
    so the real require_admin runs and checks the role → 403.
    """
    response = reader_client.delete("/books/1")
    assert response.status_code == 403

def test_me_endpoint_returns_user(admin_client):
    response = admin_client.get("/me")
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"
    assert data["name"] == "Test Admin"

def test_me_endpoint_requires_auth(public_client):
    response = public_client.get("/me")
    assert response.status_code == 401

# --- Dependency chain test ---

def test_require_admin_chains_from_get_current_user(reader_client):
    """
    require_admin calls get_current_user internally.
    reader_client overrides get_current_user → reader.
    require_admin sees role=reader → 403.
    This tests that the chain works correctly.
    """
    response = reader_client.delete("/books/2")
    assert response.status_code == 403
    assert "Admin role required" in response.json()["message"]