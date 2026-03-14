from fastapi import FastAPI, Depends, HTTPException
from typing import Optional

from models import BookCreate, BookResponse, BookUpdate
from exceptions import BookNotFoundError, DuplicateISBNError, register_exception_handlers
from middleware import RequestContextMiddleware
from dependencies import (
    PaginationParams, get_pagination,
    FakeDB, get_db,
    CurrentUser, get_current_user, require_admin,
    BookFilters,
    _books_store, _next_id,
)

app = FastAPI(title="Book API", version="0.3.0")
app.add_middleware(RequestContextMiddleware)
register_exception_handlers(app)


# ---------------------------------------------------------------
# Notice how clean the route signatures are now.
# No Query(...) boilerplate repeated everywhere.
# No auth logic inside the handler.
# The handler only does one thing: its actual job.
# ---------------------------------------------------------------

@app.get("/books", response_model=list[BookResponse])
def list_books(
    pagination: PaginationParams = Depends(get_pagination),
    filters: BookFilters = Depends(BookFilters),
    db: FakeDB = Depends(get_db),
    # No auth required on this route — public endpoint
):
    results = list(db.store.values())

    if filters.author:
        results = [b for b in results if filters.author.lower() in b["author"].lower()]
    if filters.min_year:
        results = [b for b in results if b["year"] >= filters.min_year]
    if filters.max_year:
        results = [b for b in results if b["year"] <= filters.max_year]

    return results[pagination.offset : pagination.offset + pagination.limit]


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: FakeDB = Depends(get_db),
    # Public route — no auth
):
    if book_id not in db.store:
        raise BookNotFoundError(book_id)
    return db.store[book_id]


@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(
    book: BookCreate,
    db: FakeDB = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),  # any logged-in user
):
    global _next_id

    if book.isbn:
        if any(b.get("isbn") == book.isbn for b in db.store.values()):
            raise DuplicateISBNError(book.isbn)

    new_book = {"id": _next_id, **book.model_dump()}
    db.store[_next_id] = new_book
    _next_id += 1
    return new_book


@app.delete("/books/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    db: FakeDB = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),  # admin only
):
    if book_id not in db.store:
        raise BookNotFoundError(book_id)
    del db.store[book_id]


@app.get("/me", response_model=dict)
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Returns the current authenticated user's profile."""
    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "role": current_user.role,
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.3.0"}