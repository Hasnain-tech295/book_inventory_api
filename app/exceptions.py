from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
import logging
import uuid

logger = logging.getLogger(__name__)

# one error shape 
def make_error(
    error_code: str,
    message: str,
    request_id: str,
    details: list | None = None
)-> dict:
    payload = {
        "error_code": error_code,
        "message": message,
        "request_id": request_id,
    }

    if details:
        payload["details"] = details

    return payload

# Custom Business logic exceptions
class BookNotFoundError(Exception):
    def __init__(self, book_id: int):
        self.book_id = book_id

class InvalidSearchQueryError(Exception):
    def __init__(self, query: str):
        self.query = query

class DuplicateISBNError(Exception):
    def __init__(self, isbn: str):
        self.isbn = isbn

# Register exception handlers
def register_exception_handlers(app):
    # 1. Handle our custom BookNotFoundError -> 404
    @app.exception_handler(BookNotFoundError)
    async def book_not_found_handler(request: Request, exc: BookNotFoundError):
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=404,
            content=make_error(
                error_code="BOOK_NOT_FOUND",
                message=f"Book with id={exc.book_id} not found",
                request_id=request_id,
            ),
        )

    # 2. Handle InvalidSearchQueryError -> 400
    @app.exception_handler(InvalidSearchQueryError)
    async def invalid_search_query_handler(request: Request, exc: InvalidSearchQueryError):
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=400,
            content=make_error(
                error_code="INVALID_SEARCH_QUERY",
                message=f"Empty search query provided",
                request_id=request_id,
            ),
        )

    # 3. Handle DuplicateISBNError -> 409 Conflict
    @app.exception_handler(DuplicateISBNError)
    async def duplicate_isbn_handler(request: Request, exc: DuplicateISBNError):
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=409,
            content=make_error(
                error_code="DUPLICATE_ISBN",
                message=f"A book with ISBN {exc.isbn} already exists",
                request_id=request_id,
            ),
        )

    # 4. Override the default 422 error
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", "unknown")
        details = [
            {
                "field": " -> ".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
                "type": err["type"],
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=make_error(
                error_code="VALIDATION_ERROR",
                message="Request validation failed",
                request_id=request_id,
                details=details,
            ),
        )

    # 5. Handle HTTPException(404s, 403s, etc. raised explicitly)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = getattr(request.state, "request_id", "unknown")
        # Map status code to a machine-readable error code
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            429: "RATE_LIMITED",
        }
        error_code = error_codes.get(exc.status_code, f"HTTP_{exc.status_code}")
        return JSONResponse(
            status_code=exc.status_code,
            content=make_error(
                error_code=error_code,
                message=str(exc.detail),
                request_id=request_id,
            ),
        )

    # 6. Catch-all for unhandled exception -> 500
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")

        # Log full traceback internally (skip for now)
        logger.exception(
            f"Unhandled exception | request_id={request_id} | "
            f"path={request.url.path} | error={exc}"
        )

        # Return generic message to client - never leak stack traces - WHY?
        return JSONResponse(
            status_code=500,
            content=make_error(
                error_code="INTERNAL_ERROR",
                message="An unexpected error occured. Please try again later.",
                request_id=request_id,
            ),
        )