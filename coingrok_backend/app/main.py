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

# API Routes
from app.api.routes import health, analysis, jobs, query_logs, users

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler.
    
    Manages application startup and shutdown:
    - Startup: Initialize database tables and services
    - Shutdown: Cleanup resources (if needed)
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    
    try:
        # Initialize database
        create_db_and_tables()
        logger.info("Application startup completed successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("Application shutdown completed")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered cryptocurrency analysis service using OpenAI and Grok",
    version=settings.version,
    lifespan=lifespan,
    debug=settings.debug,
)

# Setup middleware
setup_cors(app)
setup_error_handlers(app)

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