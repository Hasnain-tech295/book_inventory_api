from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title = "Book Inventory API",
    description = "A simple API to manage book inventory",
    version = "1.0.0"
)

# In-memory database
books_db: dict[int, dict] = {
    1: {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925, "price": 10.99},
    2: {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "year": 1960, "price": 12.99},
    3: {"id": 3, "title": "1984", "author": "George Orwell", "year": 1949, "price": 9.99}
}

# Pydantic model to create a book
class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=200)
    year: int = Field(..., gt=0, lt=2100)
    price: float = Field(..., gt=0)

@app.get("/books")
def list_books():
    return list(books_db.values())

@app.get("/books/{book_id}")
def get_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[book_id]

@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    new_id = max(books_db.keys()) + 1
    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "price": book.price
    } 

    books_db[new_id] = new_book
    return new_book

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    del books_db[book_id]