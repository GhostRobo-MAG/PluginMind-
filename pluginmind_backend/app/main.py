"""
PluginMind Backend API - Main Application with AI Service Registry

A production-ready FastAPI application for AI-powered processing and analysis
with plugin-style AI service registry for improved modularity.

Author: Alexandru G. Mihai
Version: 2.0.0
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

# Core imports
from app.core.config import settings
from app.core.logging import setup_logging, get_logger

# Database
from app.database import create_db_and_tables

# AI Service Registry
from app.services.service_initialization import (
    initialize_ai_services,
    cleanup_ai_services,
    register_mock_services_for_testing
)
from app.services.ai_service_interface import ai_service_registry

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
    FastAPI lifespan event handler with AI service registry initialization.
    
    Manages application startup and shutdown:
    - Startup: Validate configuration, initialize database, register AI services
    - Shutdown: Cleanup AI services and resources
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    
    try:
        # Configuration validation happens during settings import
        logger.info("Validating configuration...")
        logger.info("Configuration validation passed")
        
        # Initialize database
        logger.info("Initializing database...")
        create_db_and_tables()
        
        # Initialize AI services registry
        logger.info("Initializing AI services registry...")
        if settings.testing:
            # Use mock services in testing mode if available
            try:
                register_mock_services_for_testing()
            except:
                # Fall back to real services if mocks not available
                initialize_ai_services()
        else:
            initialize_ai_services()
        
        # Perform initial health check on AI services
        logger.info("Performing AI services health check...")
        health_results = await ai_service_registry.health_check_all()
        for service_id, is_healthy in health_results.items():
            status = "healthy" if is_healthy else "unhealthy"
            logger.info(f"  - {service_id}: {status}")
        
        # Log registered services
        registered_services = ai_service_registry.list_services()
        logger.info(f"Registered {len(registered_services)} AI services:")
        for service_id, metadata in registered_services.items():
            logger.info(
                f"  - {service_id}: {metadata.name} "
                f"(provider: {metadata.provider}, model: {metadata.model})"
            )
        
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
        
        # Cleanup AI services
        try:
            cleanup_ai_services()
            logger.info("AI services cleaned up successfully")
        except Exception as e:
            logger.warning(f"Error during AI services cleanup: {str(e)}")
        
        # Gracefully close HTTP client connections
        try:
            from app.utils.http import http_client
            await http_client.close()
            logger.info("HTTP client connections closed gracefully")
        except Exception as e:
            logger.warning(f"Error during HTTP client shutdown: {str(e)}")
        
        logger.info("Application shutdown completed")


# Initialize FastAPI application
fastapi_kwargs = {
    "title": settings.app_name,
    "description": "AI-powered cryptocurrency analysis service with plugin-style AI services",
    "version": "2.0.0",
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

# Setup middleware (order matters)
setup_error_handlers(app)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AmbientJWTAuthMiddleware)
setup_cors(app)

# Include API routers
app.include_router(health.router, tags=["health"], prefix="")
app.include_router(analysis.router, tags=["analysis"], prefix="")
app.include_router(jobs.router, tags=["jobs"], prefix="")
app.include_router(query_logs.router, tags=["logs"], prefix="")
app.include_router(users.router, tags=["users"], prefix="")

# Testing routes (only enabled in testing mode)
if settings.testing:
    app.include_router(testing.router, tags=["testing"], prefix="")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": settings.app_name,
        "version": "2.0.0",
        "description": "AI-powered cryptocurrency analysis service",
        "features": {
            "ai_service_registry": True,
            "plugin_architecture": True,
            "4d_prompt_engine": True
        },
        "docs": "/docs" if settings.debug else None,
        "health": "/health"
    }

# AI Services management endpoints
@app.get("/services")
async def list_services():
    """
    List all registered AI services.
    
    Returns information about all AI services currently registered
    in the plugin registry.
    """
    from app.services.analysis_service import analysis_service
    
    return {
        "registry_info": analysis_service.get_service_info(),
        "health_status": await analysis_service.health_check()
    }

@app.get("/services/health")
async def services_health():
    """
    Check health status of all AI services.
    
    Performs health checks on all registered AI services and returns
    their current status.
    """
    health_results = await ai_service_registry.health_check_all()
    
    all_healthy = all(health_results.values())
    
    return {
        "overall_health": "healthy" if all_healthy else "degraded",
        "services": health_results,
        "total_services": len(health_results),
        "healthy_services": sum(1 for h in health_results.values() if h),
        "unhealthy_services": sum(1 for h in health_results.values() if not h)
    }


if __name__ == "__main__":
    import uvicorn
    # Use localhost by default for security, can be overridden via environment
    host = "127.0.0.1" if not settings.debug else "0.0.0.0"  # nosec B104
    uvicorn.run(
        "app.main:app",
        host=host,
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )