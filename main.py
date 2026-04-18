from fastapi import FastAPI, HTTPException
from schemas import BookCreate

app = FastAPI()

books_db: dict[int, dict] = {
    1: {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    2: {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee"},
    3: {"id": 3, "title": "1984", "author": "George Orwell"},
}

@app.get("/books")
def get_books() -> list:
    return list(books_db.values())

@app.get("/books/{book_id}")
def get_book(book_id: int) -> dict:
    if book_id not in books_db.keys():
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    return books_db[book_id]

@app.post("/books", status_code=201)
def create_book(book: BookCreate) -> dict:
    new_id = max(books_db.keys()) + 1 if books_db else 1
    books_db[new_id] = {**book.model_dump(), "id": new_id}
    return books_db[new_id]

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books_db.keys():
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    del books_db[book_id]
    return None