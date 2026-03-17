import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Configure logging once - structured, readable output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(request_id)s | %(message)s"
)

class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Runs on EVERY request, both directions.
    Responsibilites:
    - Generate unique request_id
    - Attach to request.state  (so handlers + error handlers can read it)
    - Log incoming request
    - Measure processing time
    - Attach X-Request-ID and X-Processing_time to response headers
    - Log outgoing response
    """
    async def dispatch(self, request: Request, call_next):
        # --- INBOUND ---
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start_time = time.perf_counter()

        logger.info(
            f"→ request | id={request_id} | "
            f"{request.method} {request.url.path} | "
            f"client={request.client.host if request.client else 'unknown'}"
        )

        # --- CALL THE ACTUAL HANDLER ---
        # Any exception not caught by exception handlers will propogate here
        try:
            response = await call_next(request)
        except Exception as exc:
            # This catches exceptions that slip past exception handlers
            # (rare in FastAPI but possible in middleware-heavy stacks)
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"✗ unhandled | id={request_id} | "
                f"duration={duration:.2f}ms | error={exc}"
            )
            # Re-raise so FastAPI's global exception handler can catch it
            raise

        # --- OUTBOUND ---
        duration = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"← response | id={request_id} | "
            f"{request.method} {request.url.path} | "
            f"status={response.status_code} | "
            f"duration={duration:.2f}ms"
        )

        # Add headers so clients + load balancers can correlate logs
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Processing-Time"] = f"{duration:.2f}ms"

        return response