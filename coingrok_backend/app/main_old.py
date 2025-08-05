"""
CoinGrok Backend API

A FastAPI-based cryptocurrency analysis service that uses AI (OpenAI + Grok) to provide
intelligent crypto investment insights. Features include:

- Synchronous and asynchronous analysis endpoints
- SQLModel-based database persistence
- Query logging for usage tracking
- 4-D Prompt Engine (Deconstruct → Diagnose → Develop → Deliver)
- Comprehensive error handling and monitoring
- CORS-enabled for frontend integration

Author: Alexandru G. Mihai
Version: 1.0.0
"""

import logging
import uuid
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Annotated
from contextlib import asynccontextmanager

# Third-party imports
from xai_sdk import AsyncClient
from xai_sdk.chat import user, system
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session, select
from openai import AsyncOpenAI

# Local imports
from app.config import OPENAI_API_KEY, GROK_API_KEY
from app.ash_prompt import ASH_SYSTEM_PROMPT
from app.database import create_db_and_tables, get_session, engine
from app.models import AnalysisJob, JobStatus, QueryLog

# Configure logging for production monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# APPLICATION LIFECYCLE & INITIALIZATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler.
    
    Handles application startup and shutdown events:
    - Startup: Initialize database tables
    - Shutdown: Cleanup resources (if needed in future)
    """
    # Startup: Create database tables if they don't exist
    logger.info("Starting CoinGrok Backend...")
    create_db_and_tables()
    logger.info("Database tables initialized successfully")
    
    yield
    
    # Shutdown: Cleanup resources (placeholder for future use)
    logger.info("Shutting down CoinGrok Backend...")

# Initialize FastAPI application with metadata
app = FastAPI(
    title="CoinGrok Backend API",
    description="AI-powered cryptocurrency analysis service using OpenAI and Grok",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# Configure CORS for frontend integration
# TODO: Update allow_origins with production frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Development frontend URL
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
# ============================================================================
# API CLIENT INITIALIZATION
# ============================================================================

# Initialize AI service clients with proper error handling
try:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    xai_client = AsyncClient(api_key=GROK_API_KEY)
    logger.info("OpenAI and Grok API clients initialized successfully")
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize API clients: {str(e)}")
    logger.error("Please check your API keys in environment variables")
    raise

# ============================================================================
# LEGACY IN-MEMORY STORAGE (DEPRECATED)
# ============================================================================

# TODO: Remove this after full migration to database storage
# Legacy job storage for backward compatibility (use Redis in production)
job_store: Dict[str, dict] = {}

# ============================================================================
# REQUEST/RESPONSE MODELS & VALIDATION
# ============================================================================

class AnalysisRequest(BaseModel):
    """
    Request model for crypto analysis endpoints.
    
    Validates user input to ensure it's within acceptable limits
    and contains meaningful content for AI processing.
    """
    user_input: str = Field(
        ..., 
        min_length=1, 
        max_length=5000,
        description="User's crypto analysis query (1-5000 characters)"
    )

    @field_validator("user_input")
    @classmethod
    def validate_user_input(cls, v: str) -> str:
        """
        Validate and sanitize user input.
        
        Args:
            v: Raw user input string
            
        Returns:
            Cleaned and validated input string
            
        Raises:
            ValueError: If input is empty or whitespace only
        """
        if not v.strip():
            raise ValueError("User input cannot be empty or whitespace only")
        return v.strip()

class JobResponse(BaseModel):
    """Response model for async job creation."""
    job_id: str = Field(description="Unique identifier for the analysis job")
    status: str = Field(description="Current job status (queued, processing, completed, failed)")
    created_at: datetime = Field(description="Job creation timestamp")
    message: str = Field(description="Human-readable status message")

class JobResult(BaseModel):
    """Response model for job status and results retrieval."""
    job_id: str = Field(description="Unique job identifier")
    status: str = Field(description="Current job status")
    created_at: datetime = Field(description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    optimized_prompt: Optional[str] = Field(None, description="AI-optimized prompt from OpenAI")
    analysis: Optional[str] = Field(None, description="Final analysis result from Grok")
    error: Optional[str] = Field(None, description="Error message if job failed")

async def cleanup_old_jobs():
    """Remove jobs older than 1 hour"""
    cutoff = datetime.now() - timedelta(hours=1)
    to_remove = [
        job_id for job_id, job_data in job_store.items()
        if job_data.get("created_at", datetime.now()) < cutoff
    ]
    for job_id in to_remove:
        del job_store[job_id]
    if to_remove:
        logger.info(f"Cleaned up {len(to_remove)} old jobs")

async def process_analysis_background(job_id: str, user_input: str):
    """Background task to process analysis"""
    logger.info(f"Starting background analysis for job {job_id}")
    
    try:
        # Update job status
        job_store[job_id]["status"] = "processing_openai"
        
        # === Step 1: Get optimized prompt from OpenAI ===
        logger.info(f"Job {job_id}: Requesting prompt optimization from OpenAI")

        ash_response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": ASH_SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )

        # Validate OpenAI response
        if not ash_response.choices or not ash_response.choices[0].message.content:
            raise Exception("Empty or invalid response from OpenAI")

        optimized_prompt = ash_response.choices[0].message.content.strip()
        logger.info(f"Job {job_id}: Successfully received optimized prompt from OpenAI")

        # Update job status
        job_store[job_id]["status"] = "processing_grok"
        job_store[job_id]["optimized_prompt"] = optimized_prompt

        # === Step 2: Send optimized prompt to Grok ===
        logger.info(f"Job {job_id}: Sending optimized prompt to Grok")

        chat = xai_client.chat.create(model="grok-4-latest")
        chat.append(system("You are an AI crypto analyst."))
        chat.append(user(optimized_prompt))
        response = await chat.sample()

        # Validate Grok response
        if not hasattr(response, "content") or not response.content:
            raise Exception("Empty or invalid response from Grok")

        final_answer = response.content
        logger.info(f"Job {job_id}: Successfully received analysis from Grok")

        # Update job with final result
        job_store[job_id].update({
            "status": "completed",
            "completed_at": datetime.now(),
            "optimized_prompt": optimized_prompt,
            "analysis": final_answer,
        })

        logger.info(f"Job {job_id}: Analysis completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id}: Analysis failed with error: {str(e)}")
        
        error_detail = "Analysis failed due to internal error"
        if "rate limit" in str(e).lower():
            error_detail = "Rate limit exceeded. Please try again later."
        elif "api key" in str(e).lower() or "unauthorized" in str(e).lower():
            error_detail = "API authentication failed"
        elif "timeout" in str(e).lower():
            error_detail = "Request timeout. Please try again."
        
        job_store[job_id].update({
            "status": "failed",
            "completed_at": datetime.now(),
            "error": error_detail,
        })

async def process_analysis_background_db(job_id: str, user_input: str):
    """Background task to process analysis using database"""
    logger.info(f"Starting background analysis for job {job_id}")
    
    try:
        # Create a new session for this background task
        with Session(engine) as session:
            # Update job status
            statement = select(AnalysisJob).where(AnalysisJob.job_id == job_id)
            job = session.exec(statement).first()
            if not job:
                logger.error(f"Job {job_id} not found in database")
                return
            
            job.status = JobStatus.PROCESSING_OPENAI
            session.add(job)
            session.commit()
        
        # === Step 1: Get optimized prompt from OpenAI ===
        logger.info(f"Job {job_id}: Requesting prompt optimization from OpenAI")

        ash_response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": ASH_SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )

        # Validate OpenAI response
        if not ash_response.choices or not ash_response.choices[0].message.content:
            raise Exception("Empty or invalid response from OpenAI")

        optimized_prompt = ash_response.choices[0].message.content.strip()
        logger.info(f"Job {job_id}: Successfully received optimized prompt from OpenAI")

        # Update job status and prompt
        with Session(engine) as session:
            statement = select(AnalysisJob).where(AnalysisJob.job_id == job_id)
            job = session.exec(statement).first()
            if job:
                job.status = JobStatus.PROCESSING_GROK
                job.optimized_prompt = optimized_prompt
                session.add(job)
                session.commit()

        # === Step 2: Send optimized prompt to Grok ===
        logger.info(f"Job {job_id}: Sending optimized prompt to Grok")

        chat = xai_client.chat.create(model="grok-4-latest")
        chat.append(system("You are an AI crypto analyst."))
        chat.append(user(optimized_prompt))
        response = await chat.sample()

        # Validate Grok response
        if not hasattr(response, "content") or not response.content:
            raise Exception("Empty or invalid response from Grok")

        final_answer = response.content
        logger.info(f"Job {job_id}: Successfully received analysis from Grok")

        # Update job with final result
        with Session(engine) as session:
            statement = select(AnalysisJob).where(AnalysisJob.job_id == job_id)
            job = session.exec(statement).first()
            if job:
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now()
                job.optimized_prompt = optimized_prompt
                job.analysis = final_answer
                session.add(job)
                session.commit()

        logger.info(f"Job {job_id}: Analysis completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id}: Analysis failed with error: {str(e)}")
        
        error_detail = "Analysis failed due to internal error"
        if "rate limit" in str(e).lower():
            error_detail = "Rate limit exceeded. Please try again later."
        elif "api key" in str(e).lower() or "unauthorized" in str(e).lower():
            error_detail = "API authentication failed"
        elif "timeout" in str(e).lower():
            error_detail = "Request timeout. Please try again."
        
        # Update job with error
        with Session(engine) as session:
            statement = select(AnalysisJob).where(AnalysisJob.job_id == job_id)
            job = session.exec(statement).first()
            if job:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now()
                job.error = error_detail
                session.add(job)
                session.commit()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Clean up old jobs during health check
        await cleanup_old_jobs()
        return {"status": "ok", "active_jobs": len(job_store)}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# ============================================================================
# MAIN API ENDPOINTS
# ============================================================================

@app.post("/analyze", response_model=dict)
async def analyze(
    req: AnalysisRequest,
    session: Annotated[Session, Depends(get_session)]
):
    """
    Synchronous Crypto Analysis Endpoint
    
    Processes crypto analysis requests using the 4-D Prompt Engine:
    1. Deconstruct: Extract coin, timeframe, budget from user input
    2. Diagnose: Validate and clarify the request 
    3. Develop: Create optimized prompt via OpenAI, get analysis via Grok
    4. Deliver: Return structured insights with sentiment, news, recommendations
    
    This endpoint logs all queries for usage tracking and analytics.
    
    Args:
        req: Analysis request with user input
        session: Database session for query logging
        
    Returns:
        Dict containing optimized_prompt and final analysis
        
    Raises:
        HTTPException: For API failures, rate limits, or validation errors
    """
    logger.info(f"Starting synchronous analysis for input length: {len(req.user_input)}")
    
    # Start performance timing for monitoring
    start_time = time.time()
    
    # Initialize query log entry for usage tracking
    # TODO: Replace "test_user" with actual user ID from authentication
    query_log = QueryLog(
        user_id="test_user",  # Mock user ID for development
        user_input=req.user_input
    )

    try:
        # === Step 1: Get optimized prompt from OpenAI ===
        logger.info("Requesting prompt optimization from OpenAI")

        ash_response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": ASH_SYSTEM_PROMPT},
                {"role": "user", "content": req.user_input},
            ],
        )

        # Validate OpenAI response
        if not ash_response.choices or not ash_response.choices[0].message.content:
            logger.error("Empty or invalid response from OpenAI")
            raise HTTPException(
                status_code=502, detail="Failed to get response from OpenAI"
            )

        optimized_prompt = ash_response.choices[0].message.content.strip()
        logger.info("Successfully received optimized prompt from OpenAI")
        
        # Store optimized prompt in query log
        query_log.optimized_prompt = optimized_prompt

        # === Step 2: Send optimized prompt to Grok ===
        logger.info("Sending optimized prompt to Grok")

        chat = xai_client.chat.create(model="grok-4-latest")
        chat.append(system("You are an AI crypto analyst."))
        chat.append(user(optimized_prompt))
        response = await chat.sample()

        # Validate Grok response
        if not hasattr(response, "content") or not response.content:
            logger.error("Empty or invalid response from Grok")
            raise HTTPException(
                status_code=502, detail="Failed to get response from Grok"
            )

        final_answer = response.content
        logger.info("Successfully received analysis from Grok")
        
        # Calculate response time and update query log with success
        response_time_ms = int((time.time() - start_time) * 1000)
        query_log.ai_result = final_answer
        query_log.response_time_ms = response_time_ms
        query_log.success = True
        
        # Save query log to database
        session.add(query_log)
        session.commit()
        
        return {
            "optimized_prompt": optimized_prompt,
            "analysis": final_answer,
        }

    except HTTPException as http_exc:
        # Log failed query for HTTP exceptions
        response_time_ms = int((time.time() - start_time) * 1000)
        query_log.response_time_ms = response_time_ms
        query_log.success = False
        query_log.error_message = http_exc.detail
        
        # Save failed query log
        session.add(query_log)
        session.commit()
        
        raise
    except Exception as e:
        logger.error(f"Analysis failed with error: {str(e)}")
        
        # Log failed query for general exceptions
        response_time_ms = int((time.time() - start_time) * 1000)
        query_log.response_time_ms = response_time_ms
        query_log.success = False
        query_log.error_message = str(e)
        
        # Save failed query log
        session.add(query_log)
        session.commit()

        if "rate limit" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
            )
        elif "api key" in str(e).lower() or "unauthorized" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="API authentication failed"
            )
        elif "timeout" in str(e).lower():
            raise HTTPException(
                status_code=504,
                detail="Request timeout. Please try again.",
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Analysis failed due to internal error",
            )

@app.post("/analyze-async", response_model=JobResponse)
async def start_async_analysis(
    req: AnalysisRequest, 
    session: Annotated[Session, Depends(get_session)]
):
    """Start asynchronous analysis and return job ID"""
    job_id = str(uuid.uuid4())
    
    # Create job in database
    analysis_job = AnalysisJob(
        job_id=job_id,
        user_input=req.user_input,
        status=JobStatus.QUEUED
    )
    session.add(analysis_job)
    session.commit()
    session.refresh(analysis_job)
    
    # Start background task
    asyncio.create_task(process_analysis_background_db(job_id, req.user_input))
    
    logger.info(f"Started async analysis job {job_id}")
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        created_at=analysis_job.created_at,
        message="Analysis started. Use the job_id to check status."
    )

@app.get("/analyze-async/{job_id}", response_model=JobResult)
async def get_analysis_result(
    job_id: str,
    session: Annotated[Session, Depends(get_session)]
):
    """Get analysis result by job ID"""
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

@app.get("/jobs")
async def list_jobs(session: Annotated[Session, Depends(get_session)]):
    """List all active jobs (for debugging)"""
    statement = select(AnalysisJob).order_by(AnalysisJob.created_at.desc())
    jobs = session.exec(statement).all()
    
    return {
        "total_jobs": len(jobs),
        "jobs": {
            job.job_id: {
                "status": job.status.value,
                "created_at": job.created_at,
                "completed_at": job.completed_at
            }
            for job in jobs
        }
    }

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str, session: Annotated[Session, Depends(get_session)]):
    """Delete a specific job"""
    statement = select(AnalysisJob).where(AnalysisJob.job_id == job_id)
    job = session.exec(statement).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    session.delete(job)
    session.commit()
    return {"message": f"Job {job_id} deleted successfully"}

@app.get("/query-logs")
async def list_query_logs(
    session: Annotated[Session, Depends(get_session)],
    limit: int = 50,
    user_id: Optional[str] = None
):
    """List query logs (for debugging and analytics)"""
    statement = select(QueryLog).order_by(QueryLog.created_at.desc()).limit(limit)
    
    if user_id:
        statement = statement.where(QueryLog.user_id == user_id)
    
    query_logs = session.exec(statement).all()
    
    return {
        "total_logs": len(query_logs),
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_input": log.user_input[:100] + "..." if len(log.user_input) > 100 else log.user_input,
                "success": log.success,
                "response_time_ms": log.response_time_ms,
                "created_at": log.created_at,
                "error_message": log.error_message
            }
            for log in query_logs
        ]
    }