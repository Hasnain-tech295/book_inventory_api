from fastapi import Header, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Literal
import logging

logger = logging.getLogger(__name__)

class PaginationParams:
    def __init__(self, limit: int, offset: int):
        self.limit = limit
        self.offset = offset

def get_pagination(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return PaginationParams(limit, offset)


_books_store: dict[int, dict] = {
    1: {"id": 1, "title": "The Great Gatsby",      "author": "F. Scott Fitzgerald", "year": 1925, "genre": "Novel",   "price": 10.99, "isbn": "9780743273565"},
    2: {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee",          "year": 1960, "genre": "Novel",   "price": 12.99, "isbn": "9780061120084"},
    3: {"id": 3, "title": "1984",                  "author": "George Orwell",       "year": 1949, "genre": "Fiction", "price": 9.99,  "isbn": "9780451524935"},
}

_next_id: int = 4

class FakeDB:
    def __init__(self, store: dict):
        self.store = store
        self._closed = False

    def close(self):
        self._closed = True
        logger.debug("DB session closed")

def get_db() -> FakeDB:
    db = FakeDB(_books_store)
    try:
        yield db
    finally:
        db.close()

class CurrentUser:
    def __init__(self, user_id: int, name: str, role: str):
        self.user_id = user_id
        self.name = name
        self.role = role

    def __repr__(self):
        return f"User(id={self.user_id}, name={self.name}, role={self.role})"

# Fake token -> user mapping
FAKE_TOKENS: dict[str, CurrentUser] = {
    "token-admin": CurrentUser(user_id=1, name="Ada Lovelace", role="admin"),
    "token-reader": CurrentUser(user_id=2, name="Alan Turing", role="reader"),
}


def get_current_user(
    authorization: str | None = Header(default=None, alias="Authorization")
) -> CurrentUser:

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Authorization header must be: Bearer <token>"
        )

    token = parts[1]
    user = FAKE_TOKENS.get(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return user

def require_editor(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role not in ("editor", "admin"):
        raise HTTPException(
            status_code=403,
            detail=f"Editor role required. Your role: {current_user.role}"
        )
    return current_user

def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail=f"Admin role required. Your role: {current_user.role}"
        )
    return current_user


# 4. Query Filter Dependency

class BookFilters:
    def __init__(
        self,
        author: str | None = Query(default=None, description="Filter by author"),
        min_year: int | None = Query(default=None, ge=1, description="Min publication year"),
        max_year: int | None = Query(default=None, ge=1, description="Max publication year"),
        genre: str | None = Query(default=None, max_length=50),
        sort_by: Literal["year", "title"] = Query(default=None, max_length=50),
        order: Literal["asc", "desc"] = Query(default=None, max_length=50),
    ):
        self.author = author
        self.min_year = min_year
        self.max_year = max_year
        self.genre = genre
        self.sort_by = sort_by
        self.order = order