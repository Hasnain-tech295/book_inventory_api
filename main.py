import logging
from fastapi import FastAPI, Query, Depends
from schemas import BookCreate, BookResponse, BookUpdate
from exceptions import (
    BookNotFoundError, 
    DuplicateISBNError, 
    InvalidSearchQueryError, 
    register_exception_handlers
)
from middleware import RequestContextMiddleware

from dependencies import (
    get_pagination, PaginationParams,
    get_db, FakeDB,
    get_current_user, CurrentUser,
    require_admin, require_editor,
    BookFilters, _next_id, _books_store
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Book Inventory API",
    description="Production style error handling demo and DI",
    version="3.0.0"
)

# register middleware
app.add_middleware(RequestContextMiddleware)

# register exception handlers
register_exception_handlers(app)

# In-memory database
# books_db: dict[int, dict] = {
#     1: {"id": 1, "title": "The Great Gatsby",      "author": "F. Scott Fitzgerald", "year": 1925, "genre": "Novel",   "price": 10.99, "isbn": "9780743273565"},
#     2: {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee",          "year": 1960, "genre": "Novel",   "price": 12.99, "isbn": "9780061120084"},
#     3: {"id": 3, "title": "1984",                  "author": "George Orwell",       "year": 1949, "genre": "Fiction", "price": 9.99,  "isbn": "9780451524935"},
# }


@app.get("/books", response_model=list[BookResponse])
def get_books(
    pagination: PaginationParams = Depends(get_pagination),
    filters: BookFilters = Depends(),
    db: FakeDB = Depends(get_db),
):
    results = list(db.store.values())

    if filters.author:
        results = [b for b in results if b["author"].lower() == filters.author.lower()]

    if filters.min_year:
        results = [b for b in results if b["year"] >= filters.min_year]

    if filters.max_year:
        results = [b for b in results if b["year"] <= filters.max_year]

    if filters.genre:
        results = [b for b in results if b["genre"].lower() == filters.genre.lower()]

    if filters.sort_by:
        results = sorted(results, key=lambda b: b[filters.sort_by], reverse=(filters.order == "desc"))

    return results[filters.offset : filters.offset + filters.limit]


@app.get("/books/search", response_model=list[BookResponse])
def search_books(
    q:      str | None    = Query(default=None, description="Search across title and author"),
    pagination: PaginationParams = Depends(get_pagination),
    db: FakeDB = Depends(get_db),
):

    if not q or not q.strip():
        raise InvalidSearchQueryError(q or "")
    # One unified query param `q` — simpler and matches the assignment spec
    q_lower = q.lower()
    results = [
        b for b in db.store.values()
        if q_lower in b["title"].lower() or q_lower in b["author"].lower()
    ]
    return results[pagination.offset : pagination.offset + pagination.limit]

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: FakeDB = Depends(get_db)):
    if book_id not in db.store:
        raise BookNotFoundError(book_id)
    return db.store[book_id]

@app.post("/books", status_code=201, response_model=BookResponse)
def create_book(book: BookCreate, db: FakeDB = Depends(get_db), user: CurrentUser = Depends(require_editor)):
    global _next_id
    # Check for duplicate ISBN
    if book.isbn:
        if any(b.get("isbn") == book.isbn for b in db.store.values()):
            raise DuplicateISBNError(isbn=book.isbn)

    new_book = {"id": _next_id, **book.model_dump()}
    db.store[_next_id] = new_book
    _next_id += 1
    return new_book


@app.patch("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, update: BookUpdate, db: FakeDB = Depends(get_db), user: CurrentUser = Depends(require_editor)):
    if book_id not in db.store:
        raise BookNotFoundError(book_id)
    db.store[book_id].update(update.model_dump(exclude_unset=True))
    return db.store[book_id]


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: FakeDB = Depends(get_db), admin: CurrentUser = Depends(require_admin)):
    if book_id not in db.store:
        raise BookNotFoundError(book_id)
    del db.store[book_id]

@app.get("/me", response_model=dict)
def me(user: CurrentUser = Depends(get_current_user)):
    return {"user_id": user.user_id, "name": user.name, "role": user.role}
    
@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


# ----
# Internal 500 route - for testing the catcha-all handler
# ----
@app.get("/debug/crash")
def trigger_crash():
    raise RuntimeError("This is an intentional unhandled exception")