from fastapi import Depends, Header, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------
# 1. PAGINATION DEPENDENCY
#
# Every collection endpoint needs limit/offset.
# Without this, you copy-paste Query(...) on every route.
# With this, you write it once and inject it everywhere.
# ---------------------------------------------------------------

class PaginationParams:
    """Reusable pagination container. Inject with Depends(get_pagination)."""
    def __init__(
        self,
        limit: int = Query(default=10, ge=1, le=100, description="Max results"),
        offset: int = Query(default=0, ge=0, description="Results to skip"),
    ):
        self.limit = limit
        self.offset = offset


def get_pagination(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


# ---------------------------------------------------------------
# 2. FAKE DATABASE SESSION DEPENDENCY
#
# In Week 2 you'll replace this with a real SQLAlchemy session.
# The point now: the PATTERN — yield, then clean up.
# This is the standard pattern for any resource that needs cleanup
# (DB connections, file handles, HTTP client sessions).
# ---------------------------------------------------------------

# Simulated DB — same as before, just accessed via dependency
_books_store: dict[int, dict] = {
    1: {"id": 1, "title": "The Hobbit",   "author": "Tolkien", "year": 1937, "isbn": None},
    2: {"id": 2, "title": "Dune",          "author": "Herbert", "year": 1965, "isbn": None},
    3: {"id": 3, "title": "Neuromancer",   "author": "Gibson",  "year": 1984, "isbn": None},
}
_next_id = 4


class FakeDB:
    """
    Simulates a DB session object.
    In Week 2, this becomes a real SQLAlchemy AsyncSession.
    The interface stays the same — handlers don't change.
    """
    def __init__(self, store: dict):
        self.store = store
        self._closed = False

    def close(self):
        self._closed = True
        logger.debug("DB session closed")


def get_db() -> FakeDB:
    """
    Yield pattern:
    - Code before yield = setup (open connection)
    - yield = the value injected into the handler
    - Code after yield = cleanup (close connection, rollback on error)
    FastAPI guarantees the cleanup runs even if the handler raises.
    """
    db = FakeDB(_books_store)
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------
# 3. AUTHENTICATION DEPENDENCY
#
# Reads the Authorization header, validates the token format,
# returns the "current user" — or raises 401/403.
#
# This is a simplified version. Week 3 covers real JWT.
# The pattern here is what matters: auth is a dependency,
# not copy-pasted logic in every route.
# ---------------------------------------------------------------

class CurrentUser:
    def __init__(self, user_id: int, name: str, role: str):
        self.user_id = user_id
        self.name = name
        self.role = role

    def __repr__(self):
        return f"User(id={self.user_id}, role={self.role})"


# Fake token → user mapping (Week 3 replaces with real JWT decode)
FAKE_TOKENS: dict[str, CurrentUser] = {
    "token-admin":  CurrentUser(user_id=1, name="Ada Lovelace", role="admin"),
    "token-reader": CurrentUser(user_id=2, name="Alan Turing",  role="reader"),
}


def get_current_user(
    authorization: Optional[str] = Header(default=None)
) -> CurrentUser:
    """
    Reads Authorization header.
    Expects format: "Bearer <token>"
    Returns CurrentUser or raises 401/403.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Authorization header must be: Bearer <token>"
        )

    token = parts[1]
    user = FAKE_TOKENS.get(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return user


def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    Chains on top of get_current_user.
    Use this on routes that require admin role.
    Regular routes use get_current_user.
    Admin routes use require_admin.
    FastAPI resolves the chain automatically.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail=f"Admin role required. Your role: {current_user.role}"
        )
    return current_user


# ---------------------------------------------------------------
# 4. QUERY FILTER DEPENDENCY
#
# Bundles common filtering params into one injectable object.
# ---------------------------------------------------------------

class BookFilters:
    def __init__(
        self,
        author: Optional[str] = Query(default=None, description="Filter by author"),
        min_year: Optional[int] = Query(default=None, ge=1, description="Min publication year"),
        max_year: Optional[int] = Query(default=None, ge=1, description="Max publication year"),
    ):
        self.author = author
        self.min_year = min_year
        self.max_year = max_year