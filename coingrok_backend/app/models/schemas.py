"""
Pydantic schemas for request/response models.

Defines the API contract for all endpoints including validation,
serialization, and documentation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.core.config import settings


class AnalysisRequest(BaseModel):
    """
    Request model for crypto analysis endpoints.
    
    Validates user input to ensure it's within acceptable limits
    and contains meaningful content for AI processing.
    """
    user_input: str = Field(
        ..., 
        min_length=1, 
        max_length=settings.max_user_input_length,
        description=f"User's crypto analysis query (1-{settings.max_user_input_length} characters)"
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


class AnalysisResponse(BaseModel):
    """Response model for synchronous analysis results."""
    optimized_prompt: str = Field(description="AI-optimized prompt from OpenAI")
    analysis: str = Field(description="Final analysis result from Grok")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(description="Service status")
    active_jobs: Optional[int] = Field(None, description="Number of active background jobs")


class QueryLogSummary(BaseModel):
    """Summary model for query log entries (for debugging endpoint)."""
    id: int = Field(description="Log entry ID")
    user_id: str = Field(description="User identifier")
    user_input: str = Field(description="Truncated user input")
    success: bool = Field(description="Whether query succeeded")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    created_at: datetime = Field(description="Query timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class QueryLogsResponse(BaseModel):
    """Response model for query logs listing."""
    total_logs: int = Field(description="Number of logs returned")
    logs: list[QueryLogSummary] = Field(description="List of query log summaries")


class UserProfile(BaseModel):
    """Response model for user profile information."""
    id: int = Field(description="User database ID")
    email: str = Field(description="User email address")
    google_id: Optional[str] = Field(None, description="Google OAuth user ID")
    subscription_tier: str = Field(description="Subscription level (free, pro, premium)")
    is_active: bool = Field(description="Account active status")
    created_at: datetime = Field(description="Account creation timestamp")


class UserUsage(BaseModel):
    """Response model for user usage statistics."""
    queries_used: int = Field(description="Number of queries used in current billing period")
    queries_limit: int = Field(description="Monthly query limit based on subscription tier")
    remaining_queries: int = Field(description="Calculated remaining queries")
    subscription_tier: str = Field(description="Current subscription tier")
    can_make_query: bool = Field(description="Whether user can make another query")