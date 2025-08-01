import logging
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from xai_sdk import AsyncClient
from xai_sdk.chat import user, system
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from openai import AsyncOpenAI
from app.config import OPENAI_API_KEY, GROK_API_KEY
from app.ash_prompt import ASH_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="CoinGrok Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize API clients with error handling
try:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    xai_client = AsyncClient(api_key=GROK_API_KEY)
    logger.info("API clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize API clients: {str(e)}")
    raise

# Job storage (use Redis in production)
job_store: Dict[str, dict] = {}

class AnalysisRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=5000)

    @validator("user_input")
    def validate_user_input(cls, v: str) -> str:
        """Ensure user input is not empty or whitespace."""
        if not v.strip():
            raise ValueError("User input cannot be empty or whitespace only")
        return v.strip()

class JobResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    message: str

class JobResult(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    optimized_prompt: Optional[str] = None
    analysis: Optional[str] = None
    error: Optional[str] = None

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

@app.post("/analyze", response_model=dict)
async def analyze(req: AnalysisRequest):
    """Synchronous analysis (original endpoint)"""
    logger.info(f"Starting synchronous analysis for input length: {len(req.user_input)}")

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

        return {
            "optimized_prompt": optimized_prompt,
            "analysis": final_answer,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed with error: {str(e)}")

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
async def start_async_analysis(req: AnalysisRequest):
    """Start asynchronous analysis and return job ID"""
    job_id = str(uuid.uuid4())
    
    # Initialize job in store
    job_store[job_id] = {
        "status": "queued",
        "created_at": datetime.now(),
    }
    
    # Start background task
    asyncio.create_task(process_analysis_background(job_id, req.user_input))
    
    logger.info(f"Started async analysis job {job_id}")
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        created_at=datetime.now(),
        message="Analysis started. Use the job_id to check status."
    )

@app.get("/analyze-async/{job_id}", response_model=JobResult)
async def get_analysis_result(job_id: str):
    """Get analysis result by job ID"""
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = job_store[job_id]
    
    return JobResult(
        job_id=job_id,
        status=job_data["status"],
        created_at=job_data["created_at"],
        completed_at=job_data.get("completed_at"),
        optimized_prompt=job_data.get("optimized_prompt"),
        analysis=job_data.get("analysis"),
        error=job_data.get("error")
    )

@app.get("/jobs")
async def list_jobs():
    """List all active jobs (for debugging)"""
    return {
        "total_jobs": len(job_store),
        "jobs": {
            job_id: {
                "status": job_data["status"],
                "created_at": job_data["created_at"],
                "completed_at": job_data.get("completed_at")
            }
            for job_id, job_data in job_store.items()
        }
    }

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a specific job"""
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del job_store[job_id]
    return {"message": f"Job {job_id} deleted successfully"}