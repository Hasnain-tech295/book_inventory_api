# main.py

from fastapi import FastAPI, HTTPException, Query
from typing import Optional, Literal
from schemas import BookCreate, BookResponse, BookUpdate

app = FastAPI(
    title="Book Inventory API",
    description="API for managing book inventory",
    version="1.0.0"
)

books_db: dict[int, dict] = {
    1: {"id": 1, "title": "The Great Gatsby",      "author": "F. Scott Fitzgerald", "year": 1925, "genre": "Novel",   "price": 10.99, "isbn": "9780743273565"},
    2: {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee",          "year": 1960, "genre": "Novel",   "price": 12.99, "isbn": "9780061120084"},
    3: {"id": 3, "title": "1984",                  "author": "George Orwell",       "year": 1949, "genre": "Fiction", "price": 9.99,  "isbn": "9780451524935"},
}


@app.get("/books", response_model=list[BookResponse])
def get_books(
    genre:   Optional[str]            = Query(default=None, max_length=50),
    sort_by: Literal["year", "title"] = Query(default="year"),   # only these two values allowed
    order:   Literal["asc", "desc"]   = Query(default="asc"),    # only these two values allowed
    limit:   int                      = Query(default=10, ge=1, le=100),
    offset:  int                      = Query(default=0,  ge=0),
):
    results = list(books_db.values())

    if genre:
        results = [b for b in results if b["genre"].lower() == genre.lower()]

    results = sorted(results, key=lambda b: b[sort_by], reverse=(order == "desc"))

    return results[offset : offset + limit]


@app.get("/books/search", response_model=list[BookResponse])
def search_books(
    q:      str           = Query(min_length=1, description="Search across title and author"),
    limit:  int           = Query(default=10, ge=1, le=100),
    offset: int           = Query(default=0,  ge=0),
):
    # One unified query param `q` — simpler and matches the assignment spec
    q_lower = q.lower()
    results = [
        b for b in books_db.values()
        if q_lower in b["title"].lower() or q_lower in b["author"].lower()
    ]
    return results[offset : offset + limit]

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    return books_db[book_id]

@app.post("/books", status_code=201, response_model=BookResponse)
def create_book(book: BookCreate):
    new_id = max(books_db.keys()) + 1 if books_db else 1
    books_db[new_id] = {**book.model_dump(), "id": new_id}
    return books_db[new_id]


@app.patch("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, update: BookUpdate):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    books_db[book_id].update(update.model_dump(exclude_unset=True))
    return books_db[book_id]


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    del books_db[book_id]