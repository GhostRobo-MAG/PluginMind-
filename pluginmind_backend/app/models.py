"""
Database Models for PluginMind Backend

SQLModel-based database schema definitions for:
- Analysis job tracking (async operations)
- User management (future authentication)
- Query logging (usage analytics and monitoring)

All models use SQLModel for type safety and automatic FastAPI integration.

Author: Alexandru G. Mihai
Version: 1.0.0
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

# ============================================================================
# ENUMS & STATUS DEFINITIONS
# ============================================================================

class JobStatus(str, Enum):
    """
    Enumeration of possible analysis job states.
    
    Used to track async job progress through the AI pipeline.
    """
    QUEUED = "queued"                    # Job created, waiting to start
    PROCESSING_OPENAI = "processing_openai"  # Getting optimized prompt
    PROCESSING_GROK = "processing_grok"      # Getting final analysis
    COMPLETED = "completed"              # Successfully finished
    FAILED = "failed"                    # Error occurred

# ============================================================================
# DATABASE MODELS
# ============================================================================

class AnalysisJob(SQLModel, table=True):
    """
    Database model for tracking asynchronous analysis jobs.
    
    Stores the complete lifecycle of background analysis tasks,
    from initial request through AI processing to final results.
    Used for async endpoint (/analyze-async) job tracking.
    """
    __tablename__ = "analysis_jobs"
    
    # Primary key and unique identifier
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(unique=True, index=True, description="UUID for external job tracking")
    
    # Request data
    user_input: str = Field(description="Original user query")
    status: JobStatus = Field(default=JobStatus.QUEUED, description="Current processing status")
    
    # Timestamps for job lifecycle tracking
    created_at: datetime = Field(default_factory=datetime.now, description="Job creation time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    
    # AI processing results
    optimized_prompt: Optional[str] = Field(None, description="Prompt from OpenAI optimization")
    analysis: Optional[str] = Field(None, description="Final analysis from Grok")
    error: Optional[str] = Field(None, description="Error message if job failed")
    
    # Metadata for future features
    user_id: Optional[str] = Field(None, index=True, description="User ID for auth integration")
    cost: Optional[float] = Field(None, description="Total API cost for billing")

class User(SQLModel, table=True):
    """Model for user management (future implementation)"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Subscription info
    subscription_tier: str = Field(default="free")  # free, pro, premium
    queries_used: int = Field(default=0)
    queries_limit: int = Field(default=10)  # Monthly limit
    
    # Auth info (for future OAuth implementation)
    google_id: Optional[str] = Field(default=None, unique=True)
    is_active: bool = Field(default=True)

class QueryLog(SQLModel, table=True):
    """Model for logging all queries and responses"""
    __tablename__ = "query_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # For tracking usage per user
    user_input: str  # Original user query
    
    # AI responses
    optimized_prompt: Optional[str] = None  # From OpenAI prompt optimization
    ai_result: Optional[str] = None  # Final result from Grok
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    response_time_ms: Optional[int] = None  # Total processing time
    success: bool = Field(default=True)  # Whether the query succeeded
    error_message: Optional[str] = None  # Error details if failed
    
    # Cost tracking
    openai_cost: Optional[float] = None
    grok_cost: Optional[float] = None
    total_cost: Optional[float] = None