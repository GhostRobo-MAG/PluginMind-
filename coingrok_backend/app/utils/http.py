"""
HTTP utilities for resilient outbound API calls.

Provides retry logic, timeouts, and error handling for external service calls.
"""

import asyncio
import uuid
from typing import Any, Callable, Optional, Dict
import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ServiceUnavailableError

logger = get_logger(__name__)


class HTTPClient:
    """
    Resilient HTTP client with retry logic and configurable timeouts.
    
    Handles transient failures with exponential backoff and provides
    structured logging for debugging and monitoring.
    """
    
    def __init__(self):
        """Initialize HTTP client with configured limits and timeouts."""
        self.client = httpx.AsyncClient(
            timeout=settings.http_timeout_seconds,
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=100
            )
        )
        logger.info("HTTP client initialized with timeout=%ss", settings.http_timeout_seconds)
    
    async def request_with_retries(
        self,
        method: str,
        url: str,
        request_id: Optional[str] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with exponential backoff retry logic.
        
        Retries on transient failures (network errors, 429, 5xx responses).
        Does not retry on 4xx errors except 429.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            request_id: Optional correlation ID for logging
            **kwargs: Additional arguments passed to httpx request
            
        Returns:
            httpx.Response: Successful response
            
        Raises:
            HTTPException: 502 on permanent failure after retries
        """
        if not request_id:
            request_id = str(uuid.uuid4())[:8]
        
        last_exception = None
        
        for attempt in range(settings.http_max_retries + 1):
            try:
                logger.debug(
                    "Making HTTP request: %s %s (attempt %d/%d, request_id=%s)",
                    method.upper(), url, attempt + 1, settings.http_max_retries + 1, request_id
                )
                
                response = await self.client.request(method, url, **kwargs)
                
                # Check if response indicates success or permanent failure
                if response.status_code < 400:
                    # Success
                    if attempt > 0:
                        logger.info(
                            "HTTP request succeeded after %d retries (request_id=%s)",
                            attempt, request_id
                        )
                    return response
                elif response.status_code == 429 or 500 <= response.status_code <= 599:
                    # Transient failure - will retry
                    logger.warning(
                        "HTTP request failed with status %d, will retry (attempt %d/%d, request_id=%s)",
                        response.status_code, attempt + 1, settings.http_max_retries + 1, request_id
                    )
                    last_exception = HTTPException(
                        status_code=response.status_code,
                        detail=f"HTTP {response.status_code}: {response.text[:200]}"
                    )
                else:
                    # Permanent failure (4xx except 429)
                    logger.error(
                        "HTTP request failed permanently with status %d (request_id=%s): %s",
                        response.status_code, request_id, response.text[:200]
                    )
                    raise ServiceUnavailableError("Upstream service unavailable")
                    
            except httpx.RequestError as e:
                # Network-level error - transient
                logger.warning(
                    "HTTP request network error, will retry (attempt %d/%d, request_id=%s): %s",
                    attempt + 1, settings.http_max_retries + 1, request_id, str(e)
                )
                last_exception = e
                
            except HTTPException:
                # Re-raise our own HTTP exceptions
                raise
                
            except Exception as e:
                # Unexpected error
                logger.error(
                    "Unexpected HTTP request error (request_id=%s): %s",
                    request_id, str(e)
                )
                raise ServiceUnavailableError("Upstream service unavailable")
            
            # Calculate backoff delay for next attempt
            if attempt < settings.http_max_retries:
                delay = settings.http_retry_backoff_base * (2 ** attempt)
                logger.debug(
                    "Backing off for %.2fs before retry (request_id=%s)",
                    delay, request_id
                )
                await asyncio.sleep(delay)
        
        # All retries exhausted
        logger.error(
            "HTTP request failed after %d attempts (request_id=%s): %s",
            settings.http_max_retries + 1, request_id, str(last_exception)
        )
        raise ServiceUnavailableError("Upstream service unavailable")
    
    async def close(self):
        """Close the HTTP client and clean up connections."""
        await self.client.aclose()


# Global HTTP client instance
http_client = HTTPClient()