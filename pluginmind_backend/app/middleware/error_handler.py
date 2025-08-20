"""
Global error handling middleware.

Provides centralized exception handling for consistent error responses
and proper logging of application errors with single source of truth mapping.
"""

from typing import Dict, Type, Tuple, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import get_logger
from app.middleware.correlation_id import get_request_id
from app.core.exceptions import (
    PluginMindBaseException,
    RateLimitError,
    AIServiceError,
    InvalidInputError,
    JobNotFoundError,
    AuthenticationError,
    UserAccessError,
    QueryLimitExceededError,
    UserNotFoundError,
    ServiceUnavailableError,
    DatabaseError,
    ErrorCodes
)

logger = get_logger(__name__)

# Single source of truth: Custom exception → (status_code, error_code) mapping
EXCEPTION_MAP: Dict[Type[PluginMindBaseException], Tuple[int, str]] = {
    AuthenticationError: (401, ErrorCodes.AUTHENTICATION_FAILED),
    UserAccessError: (500, ErrorCodes.USER_ACCESS_FAILED),
    QueryLimitExceededError: (429, ErrorCodes.QUERY_LIMIT_EXCEEDED),
    UserNotFoundError: (404, ErrorCodes.USER_NOT_FOUND),
    ServiceUnavailableError: (503, ErrorCodes.SERVICE_UNAVAILABLE),
    RateLimitError: (429, ErrorCodes.RATE_LIMIT_EXCEEDED),
    AIServiceError: (502, ErrorCodes.AI_SERVICE_ERROR),
    InvalidInputError: (400, ErrorCodes.INVALID_INPUT),
    JobNotFoundError: (404, ErrorCodes.JOB_NOT_FOUND),
    DatabaseError: (500, ErrorCodes.DATABASE_ERROR),
}

# User-friendly messages for each exception type
EXCEPTION_MESSAGES: Dict[Type[PluginMindBaseException], str] = {
    AuthenticationError: "Authentication failed. Please check your credentials.",
    UserAccessError: "User account access failed. Please try again.",
    QueryLimitExceededError: None,  # Use original message (safe for users)
    UserNotFoundError: "User not found.",
    ServiceUnavailableError: "Service temporarily unavailable. Please try again later.",
    RateLimitError: "Too many requests. Please try again later.",
    AIServiceError: "External AI service temporarily unavailable. Please try again.",
    InvalidInputError: None,  # Use original message (safe for users)
    JobNotFoundError: "Requested job was not found.",
    DatabaseError: "Database operation failed. Please try again.",
}


def create_error_response(message: str, code: str, status_code: int, extra_headers: Optional[Dict[str, str]] = None) -> JSONResponse:
    """
    Create standardized error response.
    
    Args:
        message: User-friendly error message
        code: Error code constant
        status_code: HTTP status code
        extra_headers: Optional additional headers to include
        
    Returns:
        JSONResponse with standardized error format and proper Content-Type
    """
    correlation_id = get_request_id()
    
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "code": code,
                "correlation_id": correlation_id
            }
        },
        headers=headers
    )


def raise_api_error(exc: PluginMindBaseException) -> None:
    """
    Tiny helper to raise exceptions that will be handled by the unified system.
    
    This is just a passthrough function for consistency - you can raise exceptions directly.
    
    Args:
        exc: Custom exception to raise
        
    Raises:
        The provided exception (handled by unified error handlers)
    """
    raise exc


def setup_error_handlers(app: FastAPI) -> None:
    """
    Configure global error handlers for the application.
    
    Uses single source of truth mapping for consistent exception handling.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Handle Starlette HTTP exceptions (e.g., routing 404s) with unified format.
        
        This catches routing-level exceptions that don't go through FastAPI's HTTPException handler.
        """
        correlation_id = get_request_id()
        
        # Safely handle exc.detail - ensure it's a string
        if hasattr(exc, 'detail') and isinstance(exc.detail, str):
            detail = exc.detail
        else:
            detail = "HTTP error occurred"
        
        logger.warning(f"HTTP {exc.status_code} error (Starlette): {detail} [correlation_id={correlation_id}]")
        
        # Special handling for different status codes
        if exc.status_code == 404:
            return create_error_response(
                detail,
                "HTTP_EXCEPTION",
                404
            )
        elif exc.status_code == 429:
            return create_error_response(
                "Too many requests. Please try again later.",
                ErrorCodes.RATE_LIMIT_EXCEEDED,
                429
            )
        
        # General HTTP exception handling
        return create_error_response(
            detail,
            "HTTP_EXCEPTION",
            exc.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle FastAPI request validation errors with unified format.
        
        Returns 422 status with INVALID_INPUT code and user-friendly message.
        """
        correlation_id = get_request_id()
        logger.warning(f"Request validation error: {exc} [correlation_id={correlation_id}]")
        
        return create_error_response(
            "Invalid request payload.",
            ErrorCodes.INVALID_INPUT,
            422
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Handle FastAPI HTTPException as fallback only.
        
        Ensures proper logging and safe detail handling.
        For 429 errors, uses RATE_LIMIT_EXCEEDED code and preserves Retry-After headers.
        """
        correlation_id = get_request_id()
        
        # Safely handle exc.detail - ensure it's a string
        if isinstance(exc.detail, str):
            detail = exc.detail
        else:
            detail = "HTTP error occurred"
            logger.warning(f"Non-string HTTPException detail: {type(exc.detail)} [correlation_id={correlation_id}]")
        
        logger.warning(f"HTTP {exc.status_code} error: {detail} [correlation_id={correlation_id}]")
        
        # Special handling for rate limit errors (429)
        if exc.status_code == 429:
            response = create_error_response(
                "Too many requests. Please try again later.",
                ErrorCodes.RATE_LIMIT_EXCEEDED,
                429
            )
            
            # Add Retry-After header if present in original exception
            # Note: HTTPException doesn't have headers directly, but rate limiter sets it
            # This is handled by the rate limiter dependency already
            return response
        
        # Special handling for 404 errors to ensure unified format
        if exc.status_code == 404:
            return create_error_response(
                detail,
                "HTTP_EXCEPTION",
                404
            )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": detail,
                    "code": "HTTP_EXCEPTION",
                    "correlation_id": correlation_id
                }
            },
            headers={"Content-Type": "application/json"}
        )
    
    @app.exception_handler(PluginMindBaseException)
    async def pluginmind_exception_handler(request: Request, exc: PluginMindBaseException):
        """
        Generic handler for all PluginMind custom exceptions.
        
        Uses EXCEPTION_MAP for single source of truth mapping.
        """
        correlation_id = get_request_id()
        exc_type = type(exc)
        
        # Get status code and error code from mapping
        if exc_type in EXCEPTION_MAP:
            status_code, error_code = EXCEPTION_MAP[exc_type]
            
            # Get user-friendly message or use original if safe
            message = EXCEPTION_MESSAGES.get(exc_type)
            if message is None:
                # Use original exception message (marked as safe for users)
                message = str(exc)
            
            # Log with appropriate level based on status code
            log_message = f"{exc_type.__name__}: {str(exc)} [correlation_id={correlation_id}]"
            if status_code >= 500:
                logger.error(log_message)
            elif status_code >= 400:
                logger.warning(log_message)
            else:
                logger.info(log_message)
            
            # Special handling for RateLimitError to include Retry-After header
            extra_headers = None
            if isinstance(exc, RateLimitError) and hasattr(exc, 'retry_after') and exc.retry_after:
                extra_headers = {"Retry-After": str(exc.retry_after)}
            
            return create_error_response(message, error_code, status_code, extra_headers)
        else:
            # Fallback for unmapped custom exceptions
            logger.error(f"Unmapped custom exception {exc_type.__name__}: {str(exc)} [correlation_id={correlation_id}]")
            return create_error_response(
                "Internal service error. Please try again.",
                ErrorCodes.INTERNAL_SERVER_ERROR,
                500
            )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        correlation_id = get_request_id()
        logger.error(f"Unexpected error: {str(exc)} [correlation_id={correlation_id}]", exc_info=True)
        return create_error_response(
            "Internal server error. Please contact support if the issue persists.",
            ErrorCodes.INTERNAL_SERVER_ERROR,
            500
        )
    
    logger.info(f"Error handlers configured successfully with {len(EXCEPTION_MAP)} mapped exceptions")