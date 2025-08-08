"""
Analysis endpoints for crypto analysis.

Provides both synchronous and asynchronous crypto analysis endpoints
using the 4-D Prompt Engine (OpenAI + Grok integration).
"""

import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.api.dependencies import SessionDep
from app.middleware.auth import UserDep
from app.models.schemas import (
    AnalysisRequest, 
    AnalysisResponse, 
    JobResponse, 
    JobResult
)
from app.services.analysis_service import analysis_service
from app.services.user_service import user_service
from app.utils.background_tasks import create_analysis_job, process_analysis_background
from app.core.exceptions import AIServiceError, RateLimitError

logger = get_logger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(req: AnalysisRequest, session: SessionDep, user_id: UserDep):
    """
    Synchronous Crypto Analysis Endpoint (Protected)
    
    Processes crypto analysis requests using the 4-D Prompt Engine:
    1. Deconstruct: Extract coin, timeframe, budget from user input
    2. Diagnose: Validate and clarify the request 
    3. Develop: Create optimized prompt via OpenAI, get analysis via Grok
    4. Deliver: Return structured insights with sentiment, news, recommendations
    
    This endpoint requires authentication and tracks user queries for billing/limits.
    
    Args:
        req: Analysis request with user input
        session: Database session for query logging
        user_id: Authenticated user ID from JWT token
        
    Returns:
        AnalysisResponse: Contains optimized_prompt and final analysis
        
    Raises:
        HTTPException: For authentication, query limits, API failures, or validation errors
    """
    logger.info(f"Starting authenticated analysis for user: {user_id}, input length: {len(req.user_input)}")
    
    try:
        # Get or create user in database
        user = user_service.get_or_create_user(session, user_id)
        
        # Check query limits
        if not user_service.check_query_limit(user):
            raise HTTPException(
                status_code=429,
                detail=f"Query limit exceeded. Used {user.queries_used}/{user.queries_limit} queries."
            )
        
        # Increment user query count
        user = user_service.increment_user_queries(session, user)
        
        # Perform analysis with user tracking
        optimized_prompt, analysis_result = await analysis_service.perform_analysis_with_logging(
            req.user_input, session, user_id=user.google_id or user_id
        )
        
        logger.info(f"Analysis completed for user: {user.email} ({user.queries_used}/{user.queries_limit} queries used)")
        
        return AnalysisResponse(
            optimized_prompt=optimized_prompt,
            analysis=analysis_result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like query limit exceeded)
        raise
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except AIServiceError as e:
        # Check for specific error types
        error_msg = str(e).lower()
        if "authentication" in error_msg:
            raise HTTPException(status_code=401, detail=str(e))
        elif "timeout" in error_msg:
            raise HTTPException(status_code=504, detail=str(e))
        else:
            raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed with unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed due to internal error")


@router.post("/analyze-async", response_model=JobResponse)
async def start_async_analysis(req: AnalysisRequest):
    """
    Start Asynchronous Analysis Job
    
    Creates a background analysis job and returns immediately with a job ID.
    Use the job ID with GET /analyze-async/{job_id} to check status and results.
    
    Args:
        req: Analysis request with user input
        
    Returns:
        JobResponse: Job ID and initial status information
    """
    logger.info(f"Starting async analysis for input length: {len(req.user_input)}")
    
    try:
        # Create job in database
        job_id = create_analysis_job(req.user_input)
        
        # Start background processing
        asyncio.create_task(process_analysis_background(job_id, req.user_input))
        
        logger.info(f"Started async analysis job {job_id}")
        
        return JobResponse(
            job_id=job_id,
            status="queued",
            created_at=datetime.now(),
            message="Analysis started. Use the job_id to check status."
        )
        
    except Exception as e:
        logger.error(f"Failed to start async analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start analysis job")


@router.get("/analyze-async/{job_id}", response_model=JobResult)
async def get_analysis_result(job_id: str, session: SessionDep):
    """
    Get Analysis Job Results
    
    Retrieves the status and results of an asynchronous analysis job.
    
    Args:
        job_id: Unique job identifier from start_async_analysis
        session: Database session
        
    Returns:
        JobResult: Job status, results, and metadata
        
    Raises:
        HTTPException: If job is not found
    """
    from sqlmodel import select
    from app.models.database import AnalysisJob
    
    statement = select(AnalysisJob).where(AnalysisJob.job_id == job_id)
    job = session.exec(statement).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResult(
        job_id=job.job_id,
        status=job.status.value,
        created_at=job.created_at,
        completed_at=job.completed_at,
        optimized_prompt=job.optimized_prompt,
        analysis=job.analysis,
        error=job.error
    )