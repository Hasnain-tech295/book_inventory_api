from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Book Inventory API",
    description="A simple API for managing book inventory",
    version="1.0.0"
)


books_db: dict[int, dict] = {
    1: {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925, "price": 10.99},
    2: {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "year": 1960, "price": 12.99},
    3: {"id": 3, "title": "1984", "author": "George Orwell", "year": 1949, "price": 9.99},
    4: {"id": 4, "title": "Pride and Prejudice", "author": "Jane Austen", "year": 1813, "price": 8.99},
    5: {"id": 5, "title": "The Catcher in the Rye", "author": "J.D. Salinger", "year": 1951, "price": 11.99},
}

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(gt=0, le=2026)
    price: float = Field(gt=0)


@app.get("/books")
def get_all_books():
    return list(books_db.values())

@app.get("/books/{book_id}")
def get_book_by_id(book_id: int):
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[book_id]

@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    new_id = max(books_db.keys()) + 1
    books_db[new_id] = {"id": new_id, "title": book.title, "author": book.author, "year": book.year, "price": book.price}
    return books_db[new_id]

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books_db.keys():
        raise HTTPException(status_code=404, detail="Book not found")
    del books_db[book_id]
    return {"message": "Book deleted successfully"}