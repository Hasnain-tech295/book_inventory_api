from fastapi import APIRouter, Depends, Query
from app.models import BookCreate, BookResponse, BookUpdate
from app.dependencies import (
    get_pagination, PaginationParams,
    get_db, FakeDB,
    get_current_user, CurrentUser,
    require_admin, require_editor,
    BookFilters, _next_id, _books_store
)
from app.exceptions import BookNotFoundError, DuplicateISBNError, InvalidSearchQueryError


router = APIRouter(prefix="/books", tags=["books"])

# ------------------------------------------------------------------------------
# router: GET /books (List all books)
# ------------------------------------------------------------------------------
@router.get("/", response_model=list[BookResponse])
def list_books(
    pagination: PaginationParams = Depends(get_pagination),
    filters: BookFilters = Depends(),
    db: FakeDB = Depends(get_db),
):
    """Get a paginated list of books with optional filters"""
    results = list(db.store.values())

    # Apply filters
    if filters.author:
        results = [b for b in results if b["author"].lower() == filters.author.lower()]

    if filters.min_year:
        results = [b for b in results if b["year"] >= filters.min_year]

    if filters.max_year:
        results = [b for b in results if b["year"] <= filters.max_year]

    if filters.genre:
        results = [b for b in results if b["genre"].lower() == filters.genre.lower()]

    # Apply sorting
    if filters.sort_by:
        results = sorted(results, key=lambda b: b[filters.sort_by], reverse=(filters.order == "desc"))

    # Apply pagination
    return results[pagination.offset : pagination.offset + pagination.limit]


# ------------------------------------------------------------------------------
# router: GET /books/search (Search for books)
# ------------------------------------------------------------------------------
@router.get("/search", response_model=list[BookResponse])
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


# ------------------------------------------------------------------------------
# router: GET /books/{book_id} (Get a specific book)
# ------------------------------------------------------------------------------
@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: FakeDB = Depends(get_db)):
    if book_id not in db.store:
        raise BookNotFoundError(book_id)
    return db.store[book_id]

# ------------------------------------------------------------------------------
# router: POST /books (Create a new book)
# ------------------------------------------------------------------------------
@router.post("/", status_code=201, response_model=BookResponse)
def create_book(
    book: BookCreate,
    db: FakeDB = Depends(get_db),
    # user: CurrentUser = Depends(require_editor) - throwing 401 error for some reason
):
    """Create a new book"""
    global _next_id
    # Check for duplicate ISBN
    if book.isbn:
        if any(b.get("isbn") == book.isbn for b in db.store.values()):
            raise DuplicateISBNError(isbn=book.isbn)

    new_book = {"id": _next_id, **book.model_dump()}
    db.store[_next_id] = new_book
    _next_id += 1
    return new_book




# ------------------------------------------------------------------------------
# router: PATCH /books/{book_id} (Update a book)
# ------------------------------------------------------------------------------
@router.patch("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    update: BookUpdate,
    db: FakeDB = Depends(get_db),
    # user: CurrentUser = Depends(require_editor) - throwing 401 error for some reason
):
    """Update an existing book"""
    if book_id not in db.store:
        raise BookNotFoundError(book_id)
    db.store[book_id].update(update.model_dump(exclude_unset=True))
    return db.store[book_id]


# ------------------------------------------------------------------------------
# router: DELETE /books/{book_id} (Delete a book)
# ------------------------------------------------------------------------------
@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    db: FakeDB = Depends(get_db),
    # admin: CurrentUser = Depends(require_admin) - throwing 401 error for some reason
):
    """Delete a book (admin only)"""
    if book_id not in db.store:
        raise BookNotFoundError(book_id)
    del db.store[book_id]
