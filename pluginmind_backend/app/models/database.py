"""
Database models for PluginMind Backend.

SQLModel-based database schema definitions for:
- Analysis job tracking (async operations)
- User management (future authentication)
- Query logging (usage analytics and monitoring)

All models use SQLModel for type safety and automatic FastAPI integration.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from app.models.enums import JobStatus


class AnalysisResultStatus(str, Enum):
    """Status enumeration for generic analysis results."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


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
    """
    Database model for user management (future implementation).
    
    Stores user account information, subscription details, and usage tracking
    for future authentication and billing features.
    """
    __tablename__ = "users"
    
    # Primary key and basic info
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, description="User email address")
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation time")
    
    # Subscription and usage tracking
    subscription_tier: str = Field(default="free", description="Subscription level: free, pro, premium")
    queries_used: int = Field(default=0, description="Queries used in current billing period")
    queries_limit: int = Field(default=10, description="Monthly query limit based on tier")
    
    # Authentication integration (OAuth)
    google_id: Optional[str] = Field(None, unique=True, description="Google OAuth user ID")
    is_active: bool = Field(default=True, description="Account active status")


class QueryLog(SQLModel, table=True):
    """
    Database model for logging all queries and responses.
    
    Tracks every query made to the analysis endpoints for usage analytics,
    performance monitoring, and billing purposes.
    """
    __tablename__ = "query_logs"
    
    # Primary key and user tracking
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(None, index=True, description="User identifier for usage tracking")
    user_input: str = Field(description="Original user query")
    
    # AI processing results
    optimized_prompt: Optional[str] = Field(None, description="OpenAI-optimized prompt")
    ai_result: Optional[str] = Field(None, description="Final analysis result from Grok")
    
    # Performance and status tracking
    created_at: datetime = Field(default_factory=datetime.now, description="Query timestamp")
    response_time_ms: Optional[int] = Field(None, description="Total processing time in milliseconds")
    success: bool = Field(default=True, description="Whether query completed successfully")
    error_message: Optional[str] = Field(None, description="Error details if query failed")
    
    # Cost tracking for billing
    openai_cost: Optional[float] = Field(None, description="OpenAI API cost")
    grok_cost: Optional[float] = Field(None, description="Grok API cost")
    total_cost: Optional[float] = Field(None, description="Total API cost for this query")


class AnalysisResult(SQLModel, table=True):
    """
    Database model for generic AI processing results.
    
    Flexible schema to support multiple AI processing types:
    - Document summarization
    - Chatbot conversations  
    - SEO content generation
    - Custom AI workflows
    
    Replaces crypto-specific storage with generic JSON-based result storage.
    """
    __tablename__ = "analysis_results"
    
    # Primary key and identifiers
    id: Optional[int] = Field(default=None, primary_key=True)
    analysis_id: str = Field(unique=True, index=True, description="UUID for external result tracking")
    analysis_type: str = Field(index=True, description="Type of analysis: document, chat, seo, custom")
    
    # User and ownership
    user_id: Optional[str] = Field(None, index=True, description="User identifier for ownership tracking")
    
    # Input and processing data
    user_input: str = Field(description="Original user input/query")
    result_data: Optional[Dict[str, Any]] = Field(None, sa_column=Column(JSON), description="AI processing results")
    processing_metadata: Optional[Dict[str, Any]] = Field(None, sa_column=Column(JSON), description="Additional processing metadata")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, index=True, description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")
    
    # Performance tracking
    processing_time_ms: Optional[int] = Field(None, description="Total processing time")
    ai_service_used: Optional[str] = Field(None, description="AI service used for processing")
    
    # Cost tracking
    cost: Optional[float] = Field(None, description="Total API cost for this analysis")
    
    # Status and error handling
    status: AnalysisResultStatus = Field(default=AnalysisResultStatus.PENDING, description="Processing status")
    error_details: Optional[str] = Field(None, description="Error message if processing failed")