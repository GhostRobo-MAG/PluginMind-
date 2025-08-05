"""
Health check endpoints.

Provides application health monitoring and system status information
for load balancers and monitoring systems.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.models.schemas import HealthResponse

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
        raise HTTPException(status_code=503, detail="Service unavailable")