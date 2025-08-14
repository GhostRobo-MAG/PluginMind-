"""
CoinGrok Backend API - Main Application

A production-ready FastAPI application for AI-powered cryptocurrency analysis.
Refactored into a clean, modular architecture with proper separation of concerns.

Author: Alexandru G. Mihai
Version: 1.0.0
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

# Core imports
from app.core.config import settings
from app.core.logging import setup_logging, get_logger

# Database
from app.database import create_db_and_tables

# Middleware
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.request_limits import BodySizeLimitMiddleware
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.auth import AmbientJWTAuthMiddleware, get_google_issuer

# API Routes
from app.api.routes import health, analysis, jobs, query_logs, users, testing

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler with configuration validation.
    
    Manages application startup and shutdown:
    - Startup: Validate configuration, initialize database tables and services
    - Shutdown: Cleanup resources (if needed)
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    
    try:
        # Configuration validation happens during settings import
        # If we got here, configuration is valid
        logger.info("Validating configuration...")
        logger.info("Configuration validation passed")
        
        # Initialize database
        logger.info("Initializing database...")
        create_db_and_tables()
        
        logger.info("Application startup completed successfully")
        
        yield
        
    except ValueError as config_error:
        # Configuration validation error
        logger.error(f"Configuration validation failed: {str(config_error)}")
        raise
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("Starting application shutdown")
        
        # Gracefully close HTTP client connections
        try:
            from app.utils.http import http_client
            await http_client.close()
            logger.info("HTTP client connections closed gracefully")
        except Exception as e:
            logger.warning(f"Error during HTTP client shutdown: {str(e)}")
        
        logger.info("Application shutdown completed")


# Initialize FastAPI application
# Disable docs and OpenAPI in production for security
fastapi_kwargs = {
    "title": settings.app_name,
    "description": "AI-powered cryptocurrency analysis service using OpenAI and Grok",
    "version": settings.version,
    "lifespan": lifespan,
    "debug": settings.debug,
}

if not settings.debug:
    # Production mode: disable interactive docs and OpenAPI
    fastapi_kwargs.update({
        "docs_url": None,
        "redoc_url": None,
        "openapi_url": None,
    })

app = FastAPI(**fastapi_kwargs)

# Pre-warm OIDC issuer cache on startup
@app.on_event("startup")
async def _init_oidc_issuer_cache() -> None:
    try:
        issuer = get_google_issuer()
        logger.info(f"OIDC issuer cache initialized: {issuer}")
    except Exception:
        logger.warning("OIDC issuer cache initialization failed; using fallback")

# Setup middleware (order matters - CORS outermost, correlation ID early for logging)
# Middleware executes in reverse order: CORS -> Auth -> Security -> Body -> Correlation -> Routes
setup_error_handlers(app)  # Error handlers (not middleware stack)
app.add_middleware(CorrelationIdMiddleware)  # Innermost - early for logging
app.add_middleware(BodySizeLimitMiddleware)  # Body size limits
app.add_middleware(SecurityHeadersMiddleware)  # Security headers
app.add_middleware(AmbientJWTAuthMiddleware)  # Ambient JWT parsing
setup_cors(app)  # Outermost - CORS headers on all responses

# Include API routers
app.include_router(
    health.router,
    tags=["health"],
    prefix="",
)

app.include_router(
    analysis.router,
    tags=["analysis"],
    prefix="",
)

app.include_router(
    jobs.router,
    tags=["jobs"],
    prefix="",
)

app.include_router(
    query_logs.router,
    tags=["logs"],
    prefix="",
)

app.include_router(
    users.router,
    tags=["users"],
    prefix="",
)

# Testing routes (only enabled in testing mode)
if settings.testing:
    app.include_router(
        testing.router,
        tags=["testing"],
        prefix="",
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "description": "AI-powered cryptocurrency analysis service",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )