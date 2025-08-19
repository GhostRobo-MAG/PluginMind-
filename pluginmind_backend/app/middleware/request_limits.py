"""
Request size limit middleware.

Prevents oversized request payloads to protect against memory exhaustion
and denial-of-service attacks.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.core.config import settings
from app.core.logging import get_logger
from app.middleware.correlation_id import get_request_id
from app.core.exceptions import ErrorCodes

logger = get_logger(__name__)


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit request body size.
    
    Rejects requests with bodies larger than the configured limit
    with a 413 status code and safe JSON response.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.max_bytes = settings.body_max_bytes
        logger.info(f"Body size limit middleware initialized with max_bytes={self.max_bytes}")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                content_length = int(content_length)
                if content_length > self.max_bytes:
                    logger.warning(
                        f"Request rejected: body size {content_length} exceeds limit {self.max_bytes} "
                        f"from {request.client.host if request.client else 'unknown'}"
                    )
                    correlation_id = get_request_id()
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": {
                                "message": "Request body too large. Maximum size allowed is 1MB.",
                                "code": ErrorCodes.REQUEST_TOO_LARGE,
                                "correlation_id": correlation_id
                            }
                        }
                    )
            except (ValueError, TypeError):
                # Invalid Content-Length header, let it pass and potentially fail later
                pass
        
        # For requests without Content-Length, we'll let them pass
        # and rely on the body reading to enforce limits if needed
        response = await call_next(request)
        return response