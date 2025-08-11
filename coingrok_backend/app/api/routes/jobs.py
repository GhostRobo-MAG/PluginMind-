"""
Job management endpoints.

Provides endpoints for listing, monitoring, and managing analysis jobs
for debugging and administrative purposes.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.core.logging import get_logger
from app.api.dependencies import SessionDep
from app.models.database import AnalysisJob

logger = get_logger(__name__)
router = APIRouter()


@router.get("/jobs")
async def list_jobs(session: SessionDep):
    """
    List All Analysis Jobs
    
    Returns a summary of all analysis jobs for debugging and monitoring.
    Jobs are ordered by creation time (newest first).
    
    Args:
        session: Database session
        
    Returns:
        Dict containing total job count and job summaries
    """
    statement = select(AnalysisJob).order_by(AnalysisJob.created_at.desc())
    jobs = session.exec(statement).all()
    
    return {
        "total_jobs": len(jobs),
        "jobs": {
            job.job_id: {
                "status": job.status.value,
                "created_at": job.created_at,
                "completed_at": job.completed_at,
                "user_id": job.user_id,
                "has_error": bool(job.error)
            }
            for job in jobs
        }
    }


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: UUID, session: SessionDep):
    """
    Delete Analysis Job
    
    Removes a specific analysis job from the database.
    Useful for cleanup and testing purposes.
    
    Args:
        job_id: Unique job identifier
        session: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If job is not found
    """
    statement = select(AnalysisJob).where(AnalysisJob.job_id == str(job_id))
    job = session.exec(statement).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    session.delete(job)
    session.commit()
    
    logger.info(f"Deleted analysis job {job_id}")
    return {"message": f"Job {job_id} deleted successfully"}