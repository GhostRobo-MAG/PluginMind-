"""
OpenAI service for prompt optimization.

Handles all interactions with OpenAI's API for the 4-D Prompt Engine's
optimization step (Deconstruct → Diagnose → Develop).
"""

import json
import uuid
from typing import Optional
from openai import AsyncOpenAI
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging import get_logger, redact_headers
from app.core.exceptions import AIServiceError, RateLimitError, ServiceUnavailableError
from app.ash_prompt import ASH_SYSTEM_PROMPT
from app.utils.http import http_client

logger = get_logger(__name__)


class OpenAIService:
    """
    Service class for OpenAI API interactions.
    
    Handles prompt optimization using GPT-4 as part of the 4-D Prompt Engine.
    Provides resilient HTTP calls with retries, timeouts, and error handling.
    """
    
    def __init__(self):
        """Initialize OpenAI service."""
        self.api_url = settings.openai_api_url
        logger.info("OpenAI service initialized with resilient HTTP client")
    
    async def _request_with_retries(
        self, 
        payload: dict, 
        request_id: Optional[str] = None
    ) -> dict:
        """
        Make resilient HTTP request to OpenAI API with retries.
        
        Args:
            payload: Request payload for OpenAI API
            request_id: Optional correlation ID for logging
            
        Returns:
            dict: Response from OpenAI API
            
        Raises:
            HTTPException: 502 on failure after retries
        """
        if not request_id:
            request_id = str(uuid.uuid4())[:8]
        
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        # Note: Do not log raw headers; use redact_headers() for safe logging
        
        try:
            response = await http_client.request_with_retries(
                method="POST",
                url=self.api_url,
                request_id=request_id,
                headers=headers,
                json=payload
            )
            
            return response.json()
            
        except HTTPException:
            # Re-raise HTTP exceptions from retry logic
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI request (request_id={request_id}): {str(e)}")
            raise ServiceUnavailableError("Upstream service unavailable")
    
    async def optimize_prompt(self, user_input: str) -> str:
        """
        Optimize user input using the 4-D Prompt Engine.
        
        Transforms raw user input into a structured, actionable prompt
        for crypto analysis using OpenAI's GPT-4 model.
        
        Args:
            user_input: Raw user query for crypto analysis
            
        Returns:
            Optimized prompt ready for Grok analysis
            
        Raises:
            HTTPException: 502 on service failure after retries
            AIServiceError: For invalid responses or business logic errors
        """
        request_id = str(uuid.uuid4())[:8]
        
        try:
            logger.info(f"Optimizing prompt for input length: {len(user_input)} (request_id={request_id})")
            
            payload = {
                "model": settings.openai_model,
                "messages": [
                    {"role": "system", "content": ASH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_input},
                ],
            }
            
            response_data = await self._request_with_retries(payload, request_id)
            
            # Validate response structure
            if not response_data.get("choices") or not response_data["choices"][0].get("message", {}).get("content"):
                logger.error(f"Invalid OpenAI response structure (request_id={request_id})")
                raise AIServiceError("Empty or invalid response from OpenAI")
            
            optimized_prompt = response_data["choices"][0]["message"]["content"].strip()
            logger.info(f"Successfully optimized prompt via OpenAI (request_id={request_id})")
            
            return optimized_prompt
            
        except HTTPException:
            # Re-raise HTTP exceptions (already logged in retry logic)
            raise
        except AIServiceError:
            # Re-raise business logic errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in prompt optimization (request_id={request_id}): {str(e)}")
            raise ServiceUnavailableError("Upstream service unavailable")


# Global service instance
openai_service = OpenAIService()