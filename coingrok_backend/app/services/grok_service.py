"""
Grok service for crypto analysis.

Handles all interactions with Grok (xAI) API for the final analysis
step of the 4-D Prompt Engine (Deliver phase).
"""

import json
import uuid
from typing import Optional
import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging import get_logger, redact_headers
from app.core.exceptions import AIServiceError, RateLimitError, ServiceUnavailableError
from app.utils.http import http_client

logger = get_logger(__name__)


class GrokService:
    """
    Service class for Grok (xAI) API interactions.
    
    Handles crypto market analysis using Grok's AI capabilities.
    Provides resilient HTTP calls with retries, timeouts, and error handling.
    """
    
    def __init__(self):
        """Initialize Grok service."""
        self.api_url = settings.grok_api_url
        logger.info("Grok service initialized with resilient HTTP client")
    
    async def _request_with_retries(
        self, 
        payload: dict, 
        request_id: Optional[str] = None
    ) -> dict:
        """
        Make resilient HTTP request to Grok API with retries.
        
        Args:
            payload: Request payload for Grok API
            request_id: Optional correlation ID for logging
            
        Returns:
            dict: Response from Grok API
            
        Raises:
            HTTPException: 502 on failure after retries
        """
        if not request_id:
            request_id = str(uuid.uuid4())[:8]
        
        headers = {
            "Authorization": f"Bearer {settings.grok_api_key}",
            "Content-Type": "application/json",
        }
        # Note: Do not log raw headers; use redact_headers() for safe logging
        
        try:
            # Use Grok-specific timeout configuration
            grok_timeout = httpx.Timeout(
                connect=settings.grok_connect_timeout,
                read=settings.grok_timeout_seconds,
                write=settings.grok_write_timeout,
                pool=settings.grok_pool_timeout
            )
            
            response = await http_client.request_with_retries(
                method="POST",
                url=self.api_url,
                request_id=request_id,
                headers=headers,
                json=payload,
                timeout=grok_timeout
            )
            
            return response.json()
            
        except HTTPException:
            # Re-raise HTTP exceptions from retry logic
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Grok request (request_id={request_id}): {str(e)}")
            raise ServiceUnavailableError("Upstream service unavailable")
    
    async def analyze(self, optimized_prompt: str) -> str:
        """
        Perform crypto analysis using Grok AI.
        
        Takes an optimized prompt and generates comprehensive crypto
        analysis including sentiment, news, market data, and recommendations.
        
        Args:
            optimized_prompt: Pre-optimized prompt from OpenAI service
            
        Returns:
            Comprehensive crypto analysis result
            
        Raises:
            HTTPException: 502 on service failure after retries
            AIServiceError: For invalid responses or business logic errors
        """
        request_id = str(uuid.uuid4())[:8]
        
        try:
            logger.info(f"Sending optimized prompt to Grok for analysis (request_id={request_id})")
            
            payload = {
                "model": settings.grok_model,
                "messages": [
                    {"role": "system", "content": "You are an AI crypto analyst."},
                    {"role": "user", "content": optimized_prompt},
                ],
            }
            
            response_data = await self._request_with_retries(payload, request_id)
            
            # Validate response structure
            if not response_data.get("choices") or not response_data["choices"][0].get("message", {}).get("content"):
                logger.error(f"Invalid Grok response structure (request_id={request_id})")
                raise AIServiceError("Empty or invalid response from Grok")
            
            analysis_result = response_data["choices"][0]["message"]["content"]
            logger.info(f"Successfully received analysis from Grok (request_id={request_id})")
            
            return analysis_result
            
        except HTTPException:
            # Re-raise HTTP exceptions (already logged in retry logic)
            raise
        except AIServiceError:
            # Re-raise business logic errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Grok analysis (request_id={request_id}): {str(e)}")
            raise ServiceUnavailableError("Upstream service unavailable")


# Global service instance
grok_service = GrokService()