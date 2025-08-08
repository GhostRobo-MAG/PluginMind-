"""
User profile and usage endpoints.

Provides authenticated user access to their profile information,
usage statistics, and account management features.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.core.logging import get_logger
from app.api.dependencies import SessionDep
from app.middleware.auth import get_current_user
from app.services.user_service import user_service
from app.models.schemas import UserProfile, UserUsage

logger = get_logger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(session: SessionDep, user_id: str = Depends(get_current_user)):
    """
    Get Current User Profile
    
    Returns the authenticated user's profile information including
    email, subscription tier, account status, and creation date.
    
    Args:
        session: Database session
        user_id: Authenticated user ID from JWT token
        
    Returns:
        UserProfile: User profile information
        
    Raises:
        HTTPException: 404 if user not found
    """
    logger.info(f"Getting profile for user: {user_id}")
    
    # Get or create user (in case they haven't made any queries yet)
    user = user_service.get_or_create_user(session, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(
        id=user.id,
        email=user.email,
        google_id=user.google_id,
        subscription_tier=user.subscription_tier,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.get("/me/usage", response_model=UserUsage)
async def get_current_user_usage(session: SessionDep, user_id: str = Depends(get_current_user)):
    """
    Get Current User Usage Statistics
    
    Returns the authenticated user's query usage information including
    queries used, query limits, and remaining queries.
    
    Args:
        session: Database session  
        user_id: Authenticated user ID from JWT token
        
    Returns:
        UserUsage: User usage statistics
        
    Raises:
        HTTPException: 404 if user not found
    """
    logger.info(f"Getting usage stats for user: {user_id}")
    
    # Get or create user (in case they haven't made any queries yet)
    user = user_service.get_or_create_user(session, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    remaining_queries = max(0, user.queries_limit - user.queries_used)
    
    return UserUsage(
        queries_used=user.queries_used,
        queries_limit=user.queries_limit,
        remaining_queries=remaining_queries,
        subscription_tier=user.subscription_tier,
        can_make_query=user_service.check_query_limit(user)
    )