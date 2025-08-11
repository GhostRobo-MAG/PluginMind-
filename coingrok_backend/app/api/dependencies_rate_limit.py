"""
Rate limiting dependencies for FastAPI endpoints.

Provides rate limiting functionality that can be applied to specific endpoints
using FastAPI's dependency injection system.
"""

from typing import Optional
from fastapi import Request, Response, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.rate_limit import rate_limiter
from app.middleware.auth import security, verify_google_id_token

logger = get_logger(__name__)


def get_rate_limit_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Generate rate limiting key based on authentication status.
    
    For authenticated users, use user ID. For unauthenticated requests,
    use client IP address.
    
    Args:
        request: FastAPI request object
        credentials: Optional JWT credentials from Authorization header
        
    Returns:
        str: Rate limiting key in format "user:{id}" or "ip:{address}"
    """
    # Try to get authenticated user ID
    if credentials and credentials.credentials:
        try:
            user_id = verify_google_id_token(credentials.credentials)
            return f"user:{user_id}"
        except HTTPException:
            # Invalid token, fall back to IP-based limiting
            pass
    
    # Fall back to IP-based rate limiting
    client_ip = "unknown"
    if request.client and request.client.host:
        client_ip = request.client.host
    elif "x-forwarded-for" in request.headers:
        # Handle proxy/load balancer forwarded IP
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    elif "x-real-ip" in request.headers:
        client_ip = request.headers["x-real-ip"]
    
    return f"ip:{client_ip}"


async def rate_limiter_dependency(
    request: Request,
    response: Response,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    FastAPI dependency that enforces rate limiting.
    
    Applies token bucket rate limiting based on user authentication or IP address.
    Sets appropriate response headers and raises 429 on limit exceeded.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object (for setting headers)
        credentials: Optional JWT credentials from Authorization header
        
    Raises:
        HTTPException: 429 if rate limit is exceeded
    """
    # Get rate limiting key
    rate_key = get_rate_limit_key(request, credentials)
    
    # Attempt to consume 1 token
    allowed, remaining, retry_after = await rate_limiter.consume(rate_key, tokens=1)
    
    # Set rate limit headers
    response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_per_min)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    # Check if rate limit exceeded
    if not allowed:
        if retry_after:
            response.headers["Retry-After"] = str(retry_after)
        
        logger.warning(
            f"Rate limit exceeded for {rate_key} on {request.method} {request.url.path}"
        )
        
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )
    
    logger.debug(f"Rate limit check passed for {rate_key} (remaining: {remaining})")


# Dependency alias for cleaner imports
RateLimiter = Depends(rate_limiter_dependency)