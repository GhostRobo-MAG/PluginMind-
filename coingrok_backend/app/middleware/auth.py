"""
Authentication middleware for CoinGrok Backend.

Handles Google ID token verification using Google's public keys and RS256 algorithm.
Provides FastAPI dependencies for both required and optional authentication.
"""

import time
from typing import Optional, Dict, Any, Tuple
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response
import requests as http_requests
from google.auth.transport import requests
from google.oauth2 import id_token
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import AuthenticationError

logger = get_logger(__name__)

# 24-hour TTL cache for Google OpenID issuer
_ISSUER_CACHE_TTL_SECONDS: int = 86400
_issuer_cache: Tuple[Optional[str], float] = (None, 0.0)  # (issuer, ts)

security = HTTPBearer(auto_error=False)


def get_google_issuer() -> str:
    """
    Returns the Google OpenID issuer using a tiny in-memory cache.
    Refreshes at most every _ISSUER_CACHE_TTL_SECONDS.
    Falls back to 'https://accounts.google.com' on failure.
    """
    issuer, ts = _issuer_cache
    now = time.time()
    if issuer and (now - ts) < _ISSUER_CACHE_TTL_SECONDS:
        return issuer
    try:
        discovery = http_requests.get(
            "https://accounts.google.com/.well-known/openid-configuration",
            timeout=10
        ).json()
        new_issuer = discovery.get("issuer", "https://accounts.google.com")
    except Exception:
        new_issuer = "https://accounts.google.com"
    # store and return
    globals()["_issuer_cache"] = (new_issuer, now)
    return new_issuer


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
            raise AuthenticationError("Invalid audience")
        
        # Verify issuer using cached discovery
        expected_issuer = get_google_issuer()
        if idinfo['iss'] != expected_issuer:
            raise AuthenticationError("Invalid issuer")
            
        return idinfo
        
    except ValueError as e:
        # Token verification failed (includes signature, expiry, and format validation)
        raise AuthenticationError("Invalid token format")
    except AuthenticationError:
        # Re-raise our own authentication exceptions
        raise
    except Exception as e:
        # Other errors during token verification
        raise AuthenticationError("Token verification failed")


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
        raise AuthenticationError("Invalid token: missing user identifier")
        
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
        raise AuthenticationError("Authentication required. Please provide a valid JWT token in the Authorization header.")
    
    try:
        user_id = verify_google_id_token(credentials.credentials)
        logger.debug("Authentication successful")
        return user_id
    except AuthenticationError as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected authentication error: {str(e)}")
        raise AuthenticationError("Authentication failed due to invalid token")


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


class AmbientJWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Non-blocking JWT authentication middleware.
    
    Parses Bearer JWT token if present and sets request.state.user.
    Does not enforce authentication - that remains in route dependencies.
    """
    
    def __init__(self, app):
        super().__init__(app)
        logger.info("Ambient JWT auth middleware initialized")
    
    async def dispatch(self, request: StarletteRequest, call_next) -> Response:
        """
        Parse JWT token if present and set request state.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or application handler
            
        Returns:
            Response: HTTP response with user state potentially set
        """
        # Initialize request state
        request.state.user = None
        
        # Check for Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            
            try:
                # Verify token and set user in request state
                user_id = verify_google_id_token(token)
                request.state.user = user_id
                logger.debug("Set ambient user in request state")
            except HTTPException:
                # Invalid token - just log and continue (non-blocking)
                logger.debug("Invalid JWT token in Authorization header, continuing without auth")
            except Exception as e:
                # Unexpected error - log and continue
                logger.warning(f"Unexpected error parsing JWT token: {str(e)}")
        
        # Continue processing
        response = await call_next(request)
        return response


# Dependency aliases for cleaner imports
UserDep = Depends(get_current_user)
OptionalUserDep = Depends(get_current_user_optional)