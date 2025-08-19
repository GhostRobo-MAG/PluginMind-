"""
Analysis endpoints for crypto analysis.

Provides both synchronous and asynchronous crypto analysis endpoints
using the 4-D Prompt Engine (OpenAI + Grok integration).
"""

import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from app.core.logging import get_logger
from app.api.dependencies import SessionDep
from app.middleware.auth import get_current_user
from app.api.dependencies_rate_limit import RateLimiter
from app.models.schemas import (
    AnalysisRequest, 
    AnalysisResponse, 
    JobResponse, 
    JobResult
)
from app.services.analysis_service import analysis_service
from app.services.user_service import user_service
from app.utils.background_tasks import create_analysis_job, process_analysis_background
from app.core.exceptions import (
    AIServiceError, 
    RateLimitError, 
    UserAccessError, 
    QueryLimitExceededError,
    JobNotFoundError
)

logger = get_logger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(req: AnalysisRequest, session: SessionDep, user_id: str = Depends(get_current_user), _rate_limit=RateLimiter):
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
        try:
            user = user_service.get_or_create_user(session, user_id)
            logger.debug(f"Successfully retrieved/created user: {user.email if hasattr(user, 'email') else user_id}")
        except Exception as db_error:
            logger.error(f"Failed to get/create user {user_id}: {str(db_error)}")
            raise UserAccessError("User account access failed. Please try again.")
        
        # Check query limits
        try:
            if not user_service.check_query_limit(user):
                logger.warning(f"Query limit exceeded for user {user_id}: {user.queries_used}/{user.queries_limit}")
                raise QueryLimitExceededError(f"Query limit exceeded. Used {user.queries_used}/{user.queries_limit} queries.")
        except QueryLimitExceededError:
            raise
        except Exception as limit_error:
            logger.error(f"Failed to check query limit for user {user_id}: {str(limit_error)}")
            raise UserAccessError("Query limit check failed. Please try again.")
        
        # Increment user query count
        try:
            user = user_service.increment_user_queries(session, user)
            logger.debug(f"Incremented query count for user {user_id}: {user.queries_used}/{user.queries_limit}")
        except Exception as increment_error:
            logger.error(f"Failed to increment query count for user {user_id}: {str(increment_error)}")
            # Don't fail the request for this, just log the error
        
        # Perform analysis with user tracking
        optimized_prompt, analysis_result = await analysis_service.perform_analysis_with_logging(
            req.user_input, session, user_id=user.google_id or user_id
        )
        
        logger.info(f"Analysis completed for user: {user.email if hasattr(user, 'email') else user_id} ({user.queries_used}/{user.queries_limit} queries used)")
        
        return AnalysisResponse(
            optimized_prompt=optimized_prompt,
            analysis=analysis_result
        )
        
    except (UserAccessError, QueryLimitExceededError, RateLimitError, AIServiceError):
        # Re-raise custom exceptions (handled by error handlers)
        raise
    except Exception as e:
        logger.error(f"Analysis failed with unexpected error: {str(e)}")
        raise AIServiceError("Analysis failed due to internal error")


@router.post("/analyze-async", response_model=JobResponse)
async def start_async_analysis(req: AnalysisRequest, _rate_limit=RateLimiter):
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
        raise AIServiceError("Failed to start analysis job")


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
        raise JobNotFoundError("Job not found")
    
    return JobResult(
        job_id=job.job_id,
        status=job.status.value,
        created_at=job.created_at,
        completed_at=job.completed_at,
        optimized_prompt=job.optimized_prompt,
        analysis=job.analysis,
        error=job.error
    )