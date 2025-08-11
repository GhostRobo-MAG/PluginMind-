"""
Authentication middleware for CoinGrok Backend.

Handles Google ID token verification using Google's public keys and RS256 algorithm.
Provides FastAPI dependencies for both required and optional authentication.
"""

from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.auth.transport import requests
from google.oauth2 import id_token
from app.core.config import settings


security = HTTPBearer(auto_error=False)


def verify_google_id_token_claims(token: str) -> Dict[str, Any]:
    """
    Verify and decode Google ID token using Google's public keys with explicit validation.
    
    This helper function returns the raw claims dict for unit testing and internal use.
    
    Args:
        token: Google ID token string from Authorization header
        
    Returns:
        Dict[str, Any]: Token claims dictionary
        
    Raises:
        HTTPException: 401 if token is invalid or missing required claims
    """
    try:
        # Verify the token using Google's public keys and RS256
        # Note: Clock skew tolerance is handled internally by Google's library
        # which allows for small time differences in exp/iat/nbf claims
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.google_client_id
        )
        
        # Explicit audience validation
        token_audience = idinfo.get("aud")
        if token_audience != settings.google_client_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid audience"
            )
        
        # Verify issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: wrong issuer"
            )
            
        return idinfo
        
    except ValueError as e:
        # Token verification failed (includes signature, expiry, and format validation)
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    except HTTPException:
        # Re-raise our own HTTP exceptions (audience, issuer validation)
        raise
    except Exception as e:
        # Other errors during token verification
        raise HTTPException(
            status_code=401,
            detail=f"Token verification failed: {str(e)}"
        )


def verify_google_id_token(token: str) -> str:
    """
    Verify and decode Google ID token using Google's public keys.
    
    Args:
        token: Google ID token string from Authorization header
        
    Returns:
        str: User identifier (email) extracted from token claims
        
    Raises:
        HTTPException: 401 if token is invalid or missing required claims
    """
    idinfo = verify_google_id_token_claims(token)
    
    # Extract user identifier - prefer email over sub for user lookup
    user_id = idinfo.get('email')
    if not user_id:
        # Fallback to sub if email is not present
        user_id = idinfo.get('sub')
        
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: missing user identifier"
        )
        
    return user_id


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
        user_id = verify_google_id_token(credentials.credentials)
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
    
    return verify_google_id_token(credentials.credentials)


# Dependency aliases for cleaner imports
UserDep = Depends(get_current_user)
OptionalUserDep = Depends(get_current_user_optional)