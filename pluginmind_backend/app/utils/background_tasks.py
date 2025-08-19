"""
Background task processing for async analysis jobs.

Provides unified background job processing that handles the complete
analysis workflow for asynchronous operations.
"""

import uuid
from datetime import datetime
from sqlmodel import Session, select
from app.core.logging import get_logger
from app.database import engine
from app.models.database import AnalysisJob
from app.models.enums import JobStatus
from app.services.analysis_service import analysis_service

logger = get_logger(__name__)


async def process_analysis_background(job_id: str, user_input: str) -> None:
    """
    Process analysis job in the background.
    
    Unified background processing function that handles the complete
    analysis workflow for async jobs with database persistence.
    
    Args:
        job_id: Unique job identifier
        user_input: User's crypto analysis query
    """
    logger.info(f"Starting background analysis for job {job_id}")
    
    try:
        # Update job status to processing OpenAI
        with Session(engine) as session:
            statement = select(AnalysisJob).where(AnalysisJob.job_id == job_id)
            job = session.exec(statement).first()
            if not job:
                logger.error(f"Job {job_id} not found in database")
                return
            
            job.status = JobStatus.PROCESSING_OPENAI
            session.add(job)
            session.commit()
        
        # Perform complete analysis workflow
        optimized_prompt, analysis_result = await analysis_service.perform_analysis(
            user_input, job.user_id or "test_user"
        )
        
        # Update job with successful results
        with Session(engine) as session:
            statement = select(AnalysisJob).where(AnalysisJob.job_id == job_id)
            job = session.exec(statement).first()
            if job:
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now()
                job.optimized_prompt = optimized_prompt
                job.analysis = analysis_result
                session.add(job)
                session.commit()

        logger.info(f"Job {job_id}: Analysis completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id}: Analysis failed with error: {str(e)}")
        
        # Determine error type for user-friendly message
        error_detail = "Analysis failed due to internal error"
        if "rate limit" in str(e).lower():
            error_detail = "Rate limit exceeded. Please try again later."
        elif "api key" in str(e).lower() or "unauthorized" in str(e).lower():
            error_detail = "API authentication failed"
        elif "timeout" in str(e).lower():
            error_detail = "Request timeout. Please try again."
        
        # Update job with error status
        with Session(engine) as session:
            statement = select(AnalysisJob).where(AnalysisJob.job_id == job_id)
            job = session.exec(statement).first()
            if job:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now()
                job.error = error_detail
                session.add(job)
                session.commit()


def create_analysis_job(user_input: str, user_id: str = "test_user") -> str:
    """
    Create a new analysis job in the database.
    
    Args:
        user_input: User's crypto analysis query
        user_id: User identifier for tracking
        
    Returns:
        Job ID for tracking the analysis
    """
    job_id = str(uuid.uuid4())
    
    with Session(engine) as session:
        analysis_job = AnalysisJob(
            job_id=job_id,
            user_input=user_input,
            user_id=user_id,
            status=JobStatus.QUEUED
        )
        session.add(analysis_job)
        session.commit()
        session.refresh(analysis_job)
    
    logger.info(f"Created analysis job {job_id}")
    return job_id