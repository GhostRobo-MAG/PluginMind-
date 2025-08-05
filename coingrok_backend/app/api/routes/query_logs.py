"""
Query logging endpoints.

Provides endpoints for viewing and analyzing query logs for debugging,
performance monitoring, and usage analytics.
"""

from typing import Optional
from fastapi import APIRouter
from sqlmodel import select
from app.core.logging import get_logger
from app.api.dependencies import SessionDep
from app.models.database import QueryLog
from app.models.schemas import QueryLogsResponse, QueryLogSummary

logger = get_logger(__name__)
router = APIRouter()


@router.get("/query-logs", response_model=QueryLogsResponse)
async def list_query_logs(
    session: SessionDep,
    limit: int = 50,
    user_id: Optional[str] = None
):
    """
    List Query Logs
    
    Returns recent query logs for debugging and analytics.
    Useful for monitoring API usage, performance, and error patterns.
    
    Args:
        session: Database session
        limit: Maximum number of logs to return (default: 50)
        user_id: Optional filter by specific user ID
        
    Returns:
        QueryLogsResponse: List of query log summaries
    """
    statement = select(QueryLog).order_by(QueryLog.created_at.desc()).limit(limit)
    
    if user_id:
        statement = statement.where(QueryLog.user_id == user_id)
    
    query_logs = session.exec(statement).all()
    
    # Convert to summary format with truncated input for readability
    log_summaries = []
    for log in query_logs:
        # Truncate long user inputs for display
        truncated_input = log.user_input
        if len(truncated_input) > 100:
            truncated_input = truncated_input[:100] + "..."
        
        log_summaries.append(QueryLogSummary(
            id=log.id,
            user_id=log.user_id,
            user_input=truncated_input,
            success=log.success,
            response_time_ms=log.response_time_ms,
            created_at=log.created_at,
            error_message=log.error_message
        ))
    
    return QueryLogsResponse(
        total_logs=len(log_summaries),
        logs=log_summaries
    )