from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from models import BookCreate, BookResponse, BookUpdate

app = FastAPI(title="Book Inventory API", version="0.1.0")

# --- In-memory store ---
books_db: dict[int, dict] = {
    1: {"id": 1, "title": "The Hobbit",         "author": "Tolkien", "year": 1937, "isbn": None},
    2: {"id": 2, "title": "Dune",               "author": "Herbert", "year": 1965, "isbn": None},
    3: {"id": 3, "title": "Neuromancer",         "author": "Gibson",  "year": 1984, "isbn": None},
    4: {"id": 4, "title": "The Left Hand of Darkness", "author": "Le Guin", "year": 1969, "isbn": None},
}
next_id = 5  # simple auto-increment counter


# ---------------------------------------------------------------
# GET /books
# Query params: author (filter), min_year, max_year, limit, offset
# This is pagination + filtering — you'll use this pattern constantly
# ---------------------------------------------------------------
@app.get("/books", response_model=list[BookResponse])
def list_books(
    author: Optional[str] = Query(default=None, description="Filter by author name (case-insensitive)"),
    min_year: Optional[int] = Query(default=None, gt=0, description="Filter: published after this year"),
    max_year: Optional[int] = Query(default=None, gt=0, description="Filter: published before this year"),
    limit: int = Query(default=10, ge=1, le=100, description="Max results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
):
    results = list(books_db.values())

    # Apply filters
    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]
    if min_year:
        results = [b for b in results if b["year"] >= min_year]
    if max_year:
        results = [b for b in results if b["year"] <= max_year]

    # Apply pagination AFTER filtering
    return results[offset : offset + limit]


# ---------------------------------------------------------------
# GET /books/{book_id}
# Path param: book_id (int)
# ---------------------------------------------------------------
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    return books_db[book_id]


# ---------------------------------------------------------------
# POST /books
# Body: BookCreate — Pydantic validates everything before handler runs
# ---------------------------------------------------------------
@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate):
    global next_id
    new_book = {"id": next_id, **book.model_dump()}
    books_db[next_id] = new_book
    next_id += 1
    return new_book


# ---------------------------------------------------------------
# PATCH /books/{book_id}
# Partial update: only send the fields you want to change
# ---------------------------------------------------------------
@app.patch("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updates: BookUpdate):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")

    # exclude_unset=True means: only update fields the client actually sent
    # without this, Optional fields default to None and wipe existing data
    update_data = updates.model_dump(exclude_unset=True)
    books_db[book_id].update(update_data)
    return books_db[book_id]


# ---------------------------------------------------------------
# DELETE /books/{book_id}
# ---------------------------------------------------------------
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    del books_db[book_id]