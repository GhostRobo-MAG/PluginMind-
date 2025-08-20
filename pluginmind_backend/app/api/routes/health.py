"""
Health check endpoints.

Provides application health monitoring and system status information
for load balancers and monitoring systems.
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from sqlmodel import text
from app.core.logging import get_logger
from app.core.config import settings
from app.models.schemas import HealthResponse
from app.api.dependencies import SessionDep
from app.core.exceptions import ServiceUnavailableError

logger = get_logger(__name__)
router = APIRouter()

# Legacy in-memory job store for backward compatibility
# TODO: Remove after full migration to database-only jobs
job_store: Dict[str, dict] = {}


async def cleanup_old_jobs():
    """Remove jobs older than 1 hour from legacy storage."""
    cutoff = datetime.now() - timedelta(hours=1)
    to_remove = [
        job_id for job_id, job_data in job_store.items()
        if job_data.get("created_at", datetime.now()) < cutoff
    ]
    for job_id in to_remove:
        del job_store[job_id]
    if to_remove:
        logger.info(f"Cleaned up {len(to_remove)} old jobs from legacy storage")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring systems.
    
    Performs basic system health checks and cleanup operations.
    Used by load balancers and monitoring tools to verify service status.
    
    Returns:
        HealthResponse: System status and active job count
        
    Raises:
        HTTPException: If service is unavailable
    """
    try:
        # Clean up old jobs during health check
        await cleanup_old_jobs()
        
        return HealthResponse(
            status="ok",
            active_jobs=len(job_store)
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise ServiceUnavailableError("Service unavailable")


@router.get("/live")
async def liveness_check():
    """
    Liveness probe endpoint.
    
    Always returns 200 to indicate the service process is running.
    Used by orchestrators (K8s, Docker) to determine if container should be restarted.
    
    Returns:
        dict: Simple live status
    """
    return {"status": "live"}


@router.get("/ready")
async def readiness_check(session: SessionDep):
    """
    Readiness probe endpoint.
    
    Performs comprehensive checks to determine if service is ready to accept traffic.
    Checks database connectivity and required environment variables.
    
    Args:
        session: Database session for connectivity check
        
    Returns:
        dict: Readiness status with check details
        
    Raises:
        HTTPException: 503 if any readiness checks fail
    """
    checks = {}
    all_ready = True
    
    # Database connectivity check
    try:
        session.exec(text("SELECT 1"))
        checks["db"] = "ok"
        logger.debug("Database readiness check passed")
    except Exception as e:
        checks["db"] = f"failed: {str(e)}"
        all_ready = False
        logger.warning(f"Database readiness check failed: {str(e)}")
    
    # Required environment variables check
    env_issues = []
    if not settings.openai_api_key:
        env_issues.append("OPENAI_API_KEY missing")
    if not settings.grok_api_key:
        env_issues.append("GROK_API_KEY missing")
    
    if env_issues:
        checks["env"] = f"failed: {', '.join(env_issues)}"
        all_ready = False
        logger.warning(f"Environment readiness check failed: {', '.join(env_issues)}")
    else:
        checks["env"] = "ok"
        logger.debug("Environment readiness check passed")
    
    if all_ready:
        return {"status": "ready", "checks": checks}
    else:
        # For readiness checks, we still use HTTPException with custom detail format
        # This preserves the structured response format expected by orchestrators
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "checks": checks}
        )


@router.get("/version")
async def version_info():
    """
    Version information endpoint.
    
    Returns application name, version, and git SHA for deployment tracking.
    Useful for verifying deployments and debugging version-specific issues.
    
    Returns:
        dict: Application version information
    """
    return {
        "name": settings.app_name,
        "version": settings.version,
        "git_sha": os.getenv("GIT_SHA", "-")
    }


@router.get("/services")
async def services_info():
    """
    AI Services Information Endpoint.
    
    Returns information about registered AI services, their capabilities,
    and supported analysis types. Useful for clients to understand
    what processing capabilities are available.
    
    Returns:
        dict: AI service registry information and analysis types
    """
    try:
        from app.services.analysis_service import analysis_service
        from app.ash_prompt import AnalysisType
        
        # Get service info from analysis service
        service_info = analysis_service.get_service_info()
        
        # Add available analysis types
        analysis_types = {
            analysis_type.value: {
                "name": analysis_type.value.replace("_", " ").title(),
                "description": f"{analysis_type.value.replace('_', ' ').title()} processing using 4-D methodology"
            }
            for analysis_type in AnalysisType
        }
        
        return {
            "ai_services": service_info,
            "analysis_types": analysis_types,
            "endpoints": {
                "legacy_crypto": "/analyze (deprecated)",
                "generic_processing": "/process",
                "async_processing": "/analyze-async"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get services info: {str(e)}")
        return {
            "ai_services": {"error": "Failed to retrieve service information"},
            "analysis_types": {},
            "endpoints": {}
        }


@router.get("/services/health")
async def services_health():
    """
    AI Services Health Check Endpoint.
    
    Performs health checks on all registered AI services and returns
    detailed status information. Useful for monitoring AI service
    availability and troubleshooting issues.
    
    Returns:
        dict: Detailed health status of all AI services
    """
    try:
        from app.services.analysis_service import analysis_service
        
        health_status = await analysis_service.health_check()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_healthy": health_status.get("healthy", False),
            "service_details": health_status
        }
        
    except Exception as e:
        logger.error(f"Failed to check services health: {str(e)}")
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_healthy": False,
            "service_details": {"error": str(e)}
        }