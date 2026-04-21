import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

# Configure logging once - structured, readable output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

class RequestContextMiddleware(BaseHTTPMiddleware):
    # INBOUND 
    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start_time = time.perf_counter()
        
        # Log incoming request j
        logger.info(
            f"→ request | id={request_id} | "
            f"{request.method} {request.url.path} | "
            f"client={request.client.host if request.client else 'unknown'}"
        )

        # Call the actual handler
        try:
            response = await call_next(request)
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"✗ unhandled | id={request_id} | "
                f"duration={duration:.2f}ms | error={exc}"
            )
            raise  # re-raise so the exception handler still fires

        # Log outgoing response
        duration = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"← response | id={request_id} | "
            f"status={response.status_code} | "
            f"duration={duration:.2f}ms"
        )

        response.headers["X-Request_ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.2f}ms"

        return response