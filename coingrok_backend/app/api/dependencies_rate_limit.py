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
from app.utils.ip import extract_client_ip
from app.middleware.auth import security, verify_google_id_token
from app.core.exceptions import AuthenticationError

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
        except AuthenticationError:
            # Invalid token, fall back to IP-based limiting
            pass
    
    # Fall back to IP-based rate limiting using hardened extraction
    client_ip = extract_client_ip(request)
    return f"ip:{client_ip}"


async def rate_limiter_dependency(
    request: Request,
    response: Response,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    FastAPI dependency that enforces dual rate limiting.
    
    For authenticated users: enforces both user-specific and IP-specific limits.
    For unauthenticated users: enforces only IP-specific limits.
    Sets appropriate response headers and raises 429 on limit exceeded.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object (for setting headers)
        credentials: Optional JWT credentials from Authorization header
        
    Raises:
        HTTPException: 429 if rate limit is exceeded
    """
    # Check if user is authenticated
    user_id = None
    if credentials and credentials.credentials:
        try:
            user_id = verify_google_id_token(credentials.credentials)
        except AuthenticationError:
            # Invalid token, user_id remains None
            pass
    
    # Get client IP for IP-based limiting
    client_ip = extract_client_ip(request)
    ip_key = f"ip:{client_ip}"
    
    # For authenticated users: check both user and IP limits
    if user_id:
        user_key = f"user:{user_id}"
        
        # Check user limit (standard rates)
        user_allowed, user_remaining, user_retry_after = await rate_limiter.consume(user_key, tokens=1)
        
        # Check IP limit (higher rates for authenticated users)
        ip_allowed, ip_remaining, ip_retry_after = await rate_limiter.consume(
            ip_key, 
            tokens=1,
            capacity_override=settings.rate_limit_ip_burst,
            refill_rate_override=settings.rate_limit_ip_per_min / 60.0
        )
        
        # Set headers based on most restrictive limit
        if user_remaining < ip_remaining:
            response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_per_min)
            response.headers["X-RateLimit-Remaining"] = str(user_remaining)
            effective_retry_after = user_retry_after
            limiting_type = "user"
        else:
            response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_ip_per_min)
            response.headers["X-RateLimit-Remaining"] = str(ip_remaining)
            effective_retry_after = ip_retry_after
            limiting_type = "ip"
        
        # Check if either limit exceeded
        if not user_allowed or not ip_allowed:
            if effective_retry_after:
                response.headers["Retry-After"] = str(effective_retry_after)
            
            logger.warning(
                f"Rate limit exceeded for authenticated user {user_id} ({limiting_type} limit) "
                f"on {request.method} {request.url.path}"
            )
            
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
        
        logger.debug(f"Rate limit check passed for user {user_id} (user: {user_remaining}, ip: {ip_remaining})")
    
    else:
        # For unauthenticated users: check only IP limit (standard rates)
        ip_allowed, ip_remaining, ip_retry_after = await rate_limiter.consume(ip_key, tokens=1)
        
        # Set response headers
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_per_min)
        response.headers["X-RateLimit-Remaining"] = str(ip_remaining)
        
        # Check if limit exceeded
        if not ip_allowed:
            if ip_retry_after:
                response.headers["Retry-After"] = str(ip_retry_after)
            
            logger.warning(
                f"Rate limit exceeded for {ip_key} on {request.method} {request.url.path}"
            )
            
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
        
        logger.debug(f"Rate limit check passed for {ip_key} (remaining: {ip_remaining})")


# Dependency alias for cleaner imports
RateLimiter = Depends(rate_limiter_dependency)