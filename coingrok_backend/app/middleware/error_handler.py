"""
Global error handling middleware.

Provides centralized exception handling for consistent error responses
and proper logging of application errors.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.logging import get_logger
from app.core.exceptions import (
    CoinGrokBaseException,
    RateLimitError,
    AIServiceError,
    InvalidInputError,
    JobNotFoundError
)

logger = get_logger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """
    Configure global error handlers for the application.
    
    Sets up exception handlers for both custom exceptions and
    unexpected errors with appropriate HTTP status codes.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(request: Request, exc: RateLimitError):
        """Handle API rate limit errors."""
        logger.warning(f"Rate limit exceeded: {str(exc)}")
        return JSONResponse(
            status_code=429,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(AIServiceError)
    async def ai_service_handler(request: Request, exc: AIServiceError):
        """Handle AI service errors."""
        logger.error(f"AI service error: {str(exc)}")
        return JSONResponse(
            status_code=502,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(InvalidInputError)
    async def invalid_input_handler(request: Request, exc: InvalidInputError):
        """Handle input validation errors."""
        logger.warning(f"Invalid input: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(JobNotFoundError)
    async def job_not_found_handler(request: Request, exc: JobNotFoundError):
        """Handle job not found errors."""
        logger.warning(f"Job not found: {str(exc)}")
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(CoinGrokBaseException)
    async def coingrok_exception_handler(request: Request, exc: CoinGrokBaseException):
        """Handle general CoinGrok exceptions."""
        logger.error(f"CoinGrok error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal service error"}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    logger.info("Error handlers configured successfully")