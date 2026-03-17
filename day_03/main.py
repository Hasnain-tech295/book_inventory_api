import logging
from fastapi import FastAPI, Query
from typing import Optional

from models import BookCreate, BookResponse, BookUpdate
from exceptions import (
    BookNotFoundError,
    DuplicateISBNError,
    register_exception_handlers,
)
from middleware import RequestContextMiddleware

logger = logging.getLogger(__name__)

# --- APP ---
app = FastAPI(
    title="Book Inventory API",
    version="0.2.0",
    description="Production-style error handling demo",
)

# --- Register middleware (order matters: first registered = outermost) ---
app.add_middleware(RequestContextMiddleware)

# --- Register exception handlers ---
register_exception_handlers(app)

# --- In-memory storage ---
books_db: dict[int, dict] = {
    1: {"id": 1, "title": "The Hobbit",   "author": "Tolkien", "year": 1937, "isbn": None},
    2: {"id": 2, "title": "Dune",          "author": "Herbert", "year": 1965, "isbn": None},
}

next_id = 3   # simple incrementing ID for demo purposes

# ---------------------------------------------------------------
# Routes — notice we raise domain exceptions, not HTTPException
# The handler doesn't know or care about HTTP status codes.
# That's the exception handler's job.
# ---------------------------------------------------------------

@app.get("/books", response_model=list[BookResponse])
def list_books(
    author: Optional[str] = Query(default=None, description="Filter by author"),
    limit: int = Query(default=10, ge=1, le=100, description="Max number of books"),
    offset: int = Query(default=0, ge=0, description="Number of books to skip")
):
    """List all books with optional filtering and pagination"""
    # Filter by author if provided
    if author:
        filtered_books = [book for book in books_db.values() if book["author"].lower() == author.lower()]
    else:
        filtered_books = list(books_db.values())

    # Apply pagination
    paginated_books = filtered_books[offset: offset + limit]

    return paginated_books

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    """Get a single book by ID"""
    book = books_db.get(book_id)
    if not book:
        raise BookNotFoundError(book_id)   # ← domain exception, not HTTPException
    return book

@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate):
    """Create a new book"""
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
def update_book(book_id: int, book: BookUpdate):
    """Update an existing book"""
    if book_id not in books_db:
        raise BookNotFoundError(book_id)
    
    # Check for duplicate ISBN (if ISBN is being updated)
    if book.isbn and book.isbn != books_db[book_id].get("isbn"):
        existing = [b for b in books_db.values() if b.get("isbn") == book.isbn]
        if existing:
            raise DuplicateISBNError(book.isbn)

    update_data = book.model_dump(exclude_unset=True)
    books_db[book_id].update(update_data)
    return books_db[book_id]

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    """Delete a book by ID"""
    if book_id not in books_db:
        raise BookNotFoundError(book_id)
    del books_db[book_id]
    # return {"message": "Book deleted successfully"}
    

# ---------------------------------------------------------------
# Intentional 500 route — for testing the catch-all handler
# DELETE THIS in a real app. Never expose routes like this.
# ---------------------------------------------------------------

@app.get("/debug/crash")
def crash_route():
    """Route that intentionally raises an unhandled exception"""
    raise RuntimeError("This is a manually triggered crash for testing")