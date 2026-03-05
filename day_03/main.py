import logging
from fastapi import FastAPI, Query
from typing import Optional

from models import BookCreate, BookResponse, BookUpdate
from exceptions import (
    BookNotFoundError,
    DuplicateISBNError,
    register_exception_handlers
)

from middleware import RequestContextMiddleware

logger = logging.getLogger(__name__)

# --- App ---
app = FastAPI(
    title="Book Inventory API",
    version="1.0.0",
    description="Production-style error handling demo",
)

# --- Register middleware (order matters: first registered = outermost) ---
app.add_middleware(RequestContextMiddleware)

# --- Register exception handlers ---
register_exception_handlers(app)

# --- In-memory "database" ---
books_db: dict[int, dict] = {
    1: {"id": 1, "title": "The Hobbit",   "author": "Tolkien", "year": 1937, "isbn": None},
    2: {"id": 2, "title": "Dune",          "author": "Herbert", "year": 1965, "isbn": None},
}
next_id = 3


# ---------------------------------------------------------------
# Routes — notice we raise domain exceptions, not HTTPException
# The handler doesn't know or care about HTTP status codes.
# That's the exception handler's job.
# ---------------------------------------------------------------
@app.get("/books", response_model=list[BookResponse])
def list_books(
    author: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    results = list(books_db.values())
    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]
    return results[offset:offset + limit]


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    if book_id not in books_db:
        raise BookNotFoundError(book_id)  # ← domain exception, not HTTPException
    return books_db[book_id]


@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate):
    global next_id

    # Check for duplicate ISBN
    if book.isbn:
        existing = [b for b in books_db.values() if b.get("isbn") == book.isbn]
        if existing:
            raise DuplicateISBNError(book.isbn)

    new_book = {"id": next_id, **book.model_dump()}
    books_db[next_id] = new_book
    next_id += 1
    return new_book


@app.patch("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updates: BookUpdate):
    if book_id not in books_db:
        raise BookNotFoundError(book_id)
    update_data = updates.model_dump(exclude_unset=True)
    books_db[book_id].update(update_data)
    return books_db[book_id]


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books_db:
        raise BookNotFoundError(book_id)
    del books_db[book_id]


# ---------------------------------------------------------------
# Intentional 500 route — for testing the catch-all handler
# DELETE THIS in a real app. Never expose routes like this.
# ---------------------------------------------------------------
@app.get("/debug/crash")
def trigger_crash():
    raise RuntimeError("This is an intentional unhandled exception")