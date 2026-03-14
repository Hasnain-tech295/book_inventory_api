# Define error contract t - one place, one shape and forever

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging 

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------
# The ONE error shape your API always returns:
#
# {
#   "error":      "NOT_FOUND",          ← machine-readable code
#   "message":    "Book with id=5 not found",  ← human-readable
#   "request_id": "abc-123",            ← for log correlation
#   "details":    [...]                 ← optional, for validation errors
# }
#
# Clients write ONE error-handling function. That's the goal.
# ---------------------------------------------------------------

def make_error(
    error_code: str,
    message: str, 
    request_id: str,
    details: list | None = None
) -> dict:
    payload = {
        "error": error_code,
        "message": message,
        "request_id": request_id,
    }
    if details:
        payload["details"] = details
    return payload

# ---------------------------------------------------------------
# Custom business logic exceptions
# Raise these from your handlers instead of HTTPException directly.
# Keeps business logic decoupled from HTTP concerns.
# ---------------------------------------------------------------

class BookNotFoundError(Exception):
    def __init__(self, book_id: int):
        self.book_id = book_id

class DuplicateISBNError(Exception):
    def __init__(self, isbn: str):
        self.isbn = isbn

# ---------------------------------------------------------------
# Register all exception handlers on the app
# Call this once from main.py: register_exception_handlers(app)
# ---------------------------------------------------------------

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
    
    # 2. Handle Duplicate ISBN Error -> 409 Conflict
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
    
    # 3. Handle FastAPI default 422 validation error format
    @app.exception_handler(RequestValidationError) 
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Reformat Pydantic's verbrose error into something cleaner
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
                message="Request validation occured",
                request_id=request_id,
                details=details,
            ),
        )

    # 4. Handle HTTPException (404s, 403s, etc. raise explicitly)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = getattr(request.state, "request_id", "unknown")
        # Map status code to machine readable error code
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            429: "RATE_LIMIT_EXCEEDED",
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

    # 5. Catch-all for unhandled exceptions -> 500
    # CRITICAL: never expose internal error details to clients
    # Log everything, return nothing sensitive
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")
        # Log full traceback internally
        logger.exception(
            f"Unhandled exception | request_id={request_id} |"
            f"path={request.url.path} | error={exc}"
        )
        # Return generic message to client - never leak stack traces
        return JSONResponse(
            status_code=500,
            content=make_error(
                error_code="INTERNAL_SERVER_ERROR",
                message="Internal server error",
                request_id=request_id,
            ),
        )