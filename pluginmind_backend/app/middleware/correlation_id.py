"""
Correlation ID middleware for request tracing.

Provides request correlation IDs that can be tracked across logs and responses
for better debugging and monitoring capabilities.
"""

import re
import uuid
import contextvars
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)

# Context variables to store request information across the request lifecycle
request_id_context: contextvars.ContextVar[str] = contextvars.ContextVar('request_id', default='-')
request_route_context: contextvars.ContextVar[str] = contextvars.ContextVar('request_route', default=None)

# Regex for validating request ID format (alphanumeric, hyphens, underscores, dots)
REQUEST_ID_PATTERN = re.compile(r'^[A-Za-z0-9\-_.]{1,64}$')


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle correlation IDs and route information for request tracing.
    
    Reads incoming X-Request-ID header if present and valid,
    otherwise generates a new UUID. Also captures the request route/endpoint.
    Sets both ID and route in context for logging and adds ID to response header.
    """
    
    def __init__(self, app):
        super().__init__(app)
        logger.info("Correlation ID middleware initialized")
    
    def _get_or_generate_request_id(self, request: Request) -> str:
        """
        Extract or generate a request ID.
        
        Args:
            request: Incoming HTTP request
            
        Returns:
            str: Valid request ID (from header or newly generated)
        """
        # Try to get request ID from header
        incoming_id = request.headers.get("x-request-id")
        
        if incoming_id and self._is_valid_request_id(incoming_id):
            logger.debug(f"Using incoming request ID: {incoming_id}")
            return incoming_id
        else:
            # Generate new UUID-based request ID
            new_id = str(uuid.uuid4())
            if incoming_id:
                logger.debug(f"Invalid incoming request ID '{incoming_id}', generated new: {new_id}")
            else:
                logger.debug(f"No incoming request ID, generated new: {new_id}")
            return new_id
    
    def _is_valid_request_id(self, request_id: str) -> bool:
        """
        Validate request ID format.
        
        Args:
            request_id: Request ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return (
            isinstance(request_id, str) and
            len(request_id) <= 64 and
            REQUEST_ID_PATTERN.match(request_id) is not None
        )
    
    def _extract_route_path(self, request: Request) -> str:
        """
        Extract the route path from the request.
        
        Args:
            request: Incoming HTTP request
            
        Returns:
            str: Route path (e.g., '/api/v1/analysis' or '/analyze')
        """
        try:
            # Get the URL path from the request as fallback
            path = str(request.url.path)
            
            # For FastAPI, the route information is available after routing happens
            # We'll store the path and update it later if route info becomes available
            return path
        except Exception:
            # If anything goes wrong, return unknown
            return 'unknown'
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with correlation ID and route handling.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or application handler
            
        Returns:
            Response: HTTP response with X-Request-ID header
        """
        # Get or generate request ID
        request_id = self._get_or_generate_request_id(request)
        
        # Extract route path
        route_path = self._extract_route_path(request)
        
        # Set request ID and route in context for logging and other components
        request_id_token = request_id_context.set(request_id)
        route_token = request_route_context.set(route_path)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        finally:
            # Clean up context
            request_id_context.reset(request_id_token)
            request_route_context.reset(route_token)


def get_request_id() -> str:
    """
    Get the current request ID from context.
    
    Returns:
        str: Current request ID or '-' if not set
    """
    return request_id_context.get('-')


def get_request_route() -> str:
    """
    Get the current request route from context.
    
    Returns:
        str: Current request route/endpoint or None if not set
    """
    return request_route_context.get(None)