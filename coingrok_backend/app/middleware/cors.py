"""
CORS middleware configuration.

Provides secure Cross-Origin Resource Sharing configuration
for frontend integration with production-ready defaults.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware with secure defaults.
    
    Sets up Cross-Origin Resource Sharing to allow frontend access
    while maintaining security through explicit allowlists.
    
    Args:
        app: FastAPI application instance
    """
    logger.info(f"Configuring CORS for origins: {settings.cors_origins}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,  # Specific frontend domains
        allow_credentials=True,  # Allow cookies and auth headers
        allow_methods=["GET", "POST", "OPTIONS"],  # Restrict to needed methods
        allow_headers=[  # Explicit header allowlist for security
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",  # For future authentication
        ],
        max_age=86400,  # Cache preflight requests for 24 hours (performance)
    )
    
    logger.info("CORS middleware configured successfully")