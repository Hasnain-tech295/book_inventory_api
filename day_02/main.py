# --- FULL CRUD API with Path params, query params and response models ---
from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from models import BookCreate, BookResponse, BookUpdate

app = FastAPI(
    title="Book Inventory API",
    version="1.0.0"
)

# In-memory database simulation
books_db: dict[int, dict] = {
    1: {
        "id": 1,
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "year": 1979,
        "isbn": "9780345391803"
    },
    2: {
        "id": 2,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "isbn": "9780618260274"
    },
    3: {
        "id": 3,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "isbn": "9780441172719"
    },
    4: {
        "id": 4,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "isbn": "9780618260274"
    },
    5: {
        "id": 5,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "isbn": "9780441172719"
    },
    6: {
        "id": 6,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "isbn": "9780618260274"
    },
    7: {
        "id": 7,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "isbn": "9780441172719"
    },
    8: {
        "id": 8,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "isbn": "9780618260274"
    },
    9: {
        "id": 9,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "isbn": "9780441172719"
    },
    10: {
        "id": 10,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "isbn": "9780618260274"
    },
    11: {
        "id": 11,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "isbn": "9780441172719"
    },
    12: {
        "id": 12,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "isbn": "9780618260274"
    },
    13: {
        "id": 13,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "isbn": "9780441172719"
    },
    14: {
        "id": 14,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "isbn": "9780618260274"
    },
    15: {
        "id": 15,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "isbn": "9780441172719"
    },
    16: {
        "id": 16,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "isbn": "9780618260274"
    },
    17: {
        "id": 17,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "isbn": "9780441172719"
    },
    18: {
        "id": 18,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "isbn": "9780618260274"
    },
    19: {
        "id": 19,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "isbn": "9780441172719"
    },
    20: {
        "id": 20,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "isbn": "9780618260274"
    }
}

# ---------------------------------------------------------------
# GET /books
# Query params: author (filter), min_year, max_year, limit, offset
# This is pagination + filtering — you'll use this pattern constantly
# ---------------------------------------------------------------
@app.get("/books", response_model=list[BookResponse])
def get_books(
    author: Optional[str] = Query(default=None, description="Filter by author"),
    min_year: Optional[int] = Query(default=None, gt=0, le=2100, description="Filter by minimum year"),
    max_year: Optional[int] = Query(default=None, gt=0, le=2100, description="Filter by maximum year"),
    limit: int = Query(default=10, gt=0, description="Number of books to return"),
    offset: int = Query(default=0, description="Number of books to skip")
):
    results = list(books_db.values())

    # Apply filters
    if author:
        results = [book for book in results if author.lower() in book["author"].lower()]
    if min_year:
        results = [book for book in results if book["year"] >= min_year]
    if max_year:
        results = [book for book in results if book["year"] <= max_year]

    # Apply pagination AFTER filtering
    return results[offset: offset + limit]


# ---------------------------------------------------------------
# GET /books/{book_id}
# Path param: book_id (int)
# ---------------------------------------------------------------
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    if book_id not in books_db.keys():
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[book_id]


# ---------------------------------------------------------------
# POST /books
# Body: BookCreate — Pydantic validates everything before handler runs
# ---------------------------------------------------------------
@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate):
    next_id = max(books_db.keys()) + 1 if books_db else 1
    new_book = {"id": next_id, **book.model_dump()}
    books_db[next_id] = new_book
    return new_book


# ---------------------------------------------------------------
# PATCH /books/{book_id}
# Partial update: only send the fields you want to change
# ---------------------------------------------------------------
@app.patch("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, update_data: BookUpdate):
    if book_id not in books_db.keys():
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    
    # exclude id from update_data
    # exclude_unset = True means: only update fields the client actually sent
    # without this, Optional fields default to None and would overwrite existing data
    update_data = update_data.model_dump(exclude_unset=True)
    books_db[book_id].update(update_data)
    return books_db[book_id]

# ---------------------------------------------------------------
# DELETE /books/{book_id}
# ---------------------------------------------------------------
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books_db.keys():
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    del books_db[book_id]
    return