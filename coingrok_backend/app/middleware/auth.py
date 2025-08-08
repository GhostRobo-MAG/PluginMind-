"""
Authentication middleware for CoinGrok Backend.

Handles JWT token verification for Google OAuth via Supabase integration.
Provides FastAPI dependencies for both required and optional authentication.
"""

from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings


security = HTTPBearer(auto_error=False)


def verify_supabase_token(token: str) -> str:
    """
    Verify and decode Supabase JWT token.
    
    Args:
        token: JWT token string from Authorization header
        
    Returns:
        str: User ID extracted from token claims
        
    Raises:
        HTTPException: 401 if token is invalid or missing required claims
    """
    try:
        # Decode JWT using the secret from config
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Extract user ID from token claims
        user_id: str = payload.get("sub")
        if not user_id:
            # Fallback to email if sub is not present
            user_id = payload.get("email")
            
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user identifier"
            )
            
        return user_id
        
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    FastAPI dependency for required authentication.
    
    Extracts and verifies JWT token from Authorization header.
    
    Returns:
        str: User ID from verified token
        
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    
    if not credentials:
        logger.warning("Authentication failed: Missing Authorization header")
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid JWT token in the Authorization header."
        )
    
    try:
        user_id = verify_supabase_token(credentials.credentials)
        logger.debug(f"Authentication successful for user: {user_id}")
        return user_id
    except HTTPException as e:
        logger.warning(f"Authentication failed: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed due to invalid token"
        )


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    FastAPI dependency for optional authentication.
    
    Returns None if no token is provided, otherwise verifies the token.
    
    Returns:
        Optional[str]: User ID from verified token, or None if no token
        
    Raises:
        HTTPException: 401 if token exists but is invalid
    """
    if not credentials:
        return None
    
    return verify_supabase_token(credentials.credentials)


# Dependency aliases for cleaner imports
UserDep = Depends(get_current_user)
OptionalUserDep = Depends(get_current_user_optional)