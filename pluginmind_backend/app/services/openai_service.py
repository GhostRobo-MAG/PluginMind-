"""
OpenAI service implementation with AIService interface.

Handles all interactions with OpenAI's API for the 4-D Prompt Engine's
optimization step (Deconstruct → Diagnose → Develop).
"""

import json
import uuid
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging import get_logger, redact_headers
from app.core.exceptions import AIServiceError, RateLimitError, ServiceUnavailableError
from app.ash_prompt import ASH_SYSTEM_PROMPT
from app.utils.http import http_client
from app.services.ai_service_interface import (
    AIService, 
    AIServiceMetadata, 
    AIServiceCapability
)

logger = get_logger(__name__)


class OpenAIService(AIService):
    """
    OpenAI service implementation with plugin interface.
    
    Handles prompt optimization using GPT models as part of the 4-D Prompt Engine.
    Provides resilient HTTP calls with retries, timeouts, and error handling.
    """
    
    def __init__(self):
        """Initialize OpenAI service with configuration."""
        self.api_url = settings.openai_api_url
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key
        
        # Service metadata
        # GPT-5 only supports temperature=1, other models can use 0.7
        default_temperature = 1.0 if self.model.startswith("gpt-5") else 0.7
        
        self._metadata = AIServiceMetadata(
            name="OpenAI AI Service",
            provider="OpenAI",
            version="1.0.0",
            capabilities=[
                AIServiceCapability.PROMPT_OPTIMIZATION,
                AIServiceCapability.GENERIC_ANALYSIS,
                AIServiceCapability.DOCUMENT_SUMMARIZATION,
                AIServiceCapability.DOCUMENT_ANALYSIS,
                AIServiceCapability.KEY_EXTRACTION,
                AIServiceCapability.CONVERSATION_HANDLING,
                AIServiceCapability.CONTEXT_MANAGEMENT,
                AIServiceCapability.RESPONSE_GENERATION,
                AIServiceCapability.CONTENT_OPTIMIZATION,
                AIServiceCapability.KEYWORD_ANALYSIS,
                AIServiceCapability.SEO_SCORING,
                AIServiceCapability.META_GENERATION,
                AIServiceCapability.NEWS_SUMMARIZATION
            ],
            model=self.model,
            max_tokens=2000,
            temperature=default_temperature
        )
        
        logger.info(
            f"OpenAI service initialized (model: {self.model}, "
            f"capabilities: {[c.value for c in self._metadata.capabilities]})"
        )
    
    def get_metadata(self) -> AIServiceMetadata:
        """
        Get metadata about this OpenAI service.
        
        Returns:
            AIServiceMetadata describing the service
        """
        return self._metadata
    
    async def health_check(self) -> bool:
        """
        Check if OpenAI service is healthy and available.
        
        Performs a minimal API call to verify connectivity and authentication.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Simple health check - minimal payload
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "Hi"}
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            response = await http_client.request_with_retries(
                method="POST",
                url=self.api_url,
                headers=headers,
                json=payload
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {str(e)}")
            return False
    
    async def validate_input(self, input_text: str) -> bool:
        """
        Validate input for prompt optimization.
        
        Args:
            input_text: User input to validate
            
        Returns:
            True if input is valid for processing
        """
        if not input_text or not input_text.strip():
            return False
        
        # Check input length constraints
        if len(input_text) > settings.max_user_input_length:
            logger.warning(f"Input exceeds maximum length: {len(input_text)}")
            return False
        
        return True
    
    async def prepare_request(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare OpenAI API request payload.
        
        Args:
            input_text: User input for optimization
            **kwargs: Additional parameters (system_prompt, temperature, etc.)
            
        Returns:
            Prepared request payload for OpenAI API
        """
        system_prompt = kwargs.get("system_prompt", ASH_SYSTEM_PROMPT)
        temperature = kwargs.get("temperature", self._metadata.temperature)
        max_tokens = kwargs.get("max_tokens", self._metadata.max_tokens)
        
        # Minimal payload - let OpenAI use defaults for GPT-5
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text},
            ]
        }
    
    async def process(self, input_text: str, **kwargs) -> str:
        """
        Process input text through OpenAI for prompt optimization.
        
        Transforms raw user input into a structured, actionable prompt
        for crypto analysis using OpenAI's models.
        
        Args:
            input_text: Raw user query for crypto analysis
            **kwargs: Additional parameters (system_prompt, etc.)
            
        Returns:
            Optimized prompt ready for analysis
            
        Raises:
            AIServiceError: For invalid responses or business logic errors
            ServiceUnavailableError: For service failures
        """
        # Validate input
        if not await self.validate_input(input_text):
            raise AIServiceError("Invalid input for OpenAI processing")
        
        request_id = str(uuid.uuid4())[:8]
        
        try:
            logger.info(
                f"Optimizing prompt via OpenAI for input length: {len(input_text)} "
                f"(request_id={request_id})"
            )
            
            # Prepare request payload
            payload = await self.prepare_request(input_text, **kwargs)
            
            # Make API request
            response_data = await self._request_with_retries(payload, request_id)
            
            # Extract and validate response
            optimized_prompt = self._extract_response(response_data, request_id)
            
            logger.info(f"Successfully optimized prompt via OpenAI (request_id={request_id})")
            
            return optimized_prompt
            
        except HTTPException:
            # Re-raise HTTP exceptions (already logged in retry logic)
            raise
        except AIServiceError:
            # Re-raise business logic errors
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in OpenAI prompt optimization "
                f"(request_id={request_id}): {str(e)}"
            )
            raise ServiceUnavailableError("OpenAI service unavailable")
    
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
            "Authorization": f"Bearer {self.api_key}",
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
            logger.error(
                f"Unexpected error in OpenAI request (request_id={request_id}): {str(e)}"
            )
            raise ServiceUnavailableError("OpenAI service unavailable")
    
    def _extract_response(self, response_data: dict, request_id: str) -> str:
        """
        Extract and validate the response from OpenAI API.
        
        Args:
            response_data: Raw API response
            request_id: Request correlation ID
            
        Returns:
            Extracted text content
            
        Raises:
            AIServiceError: If response is invalid
        """
        # Validate response structure
        if not response_data.get("choices"):
            logger.error(f"Invalid OpenAI response: no choices (request_id={request_id})")
            raise AIServiceError("Invalid response from OpenAI: no choices")
        
        if not response_data["choices"][0].get("message"):
            logger.error(f"Invalid OpenAI response: no message (request_id={request_id})")
            raise AIServiceError("Invalid response from OpenAI: no message")
        
        content = response_data["choices"][0]["message"].get("content")
        if not content:
            logger.error(f"Invalid OpenAI response: empty content (request_id={request_id})")
            raise AIServiceError("Empty response from OpenAI")
        
        return content.strip()
    
    # Backward compatibility method
    async def optimize_prompt(self, user_input: str) -> str:
        """
        Legacy method for prompt optimization.
        
        Maintained for backward compatibility with existing code.
        Delegates to the process() method.
        
        Args:
            user_input: Raw user query for crypto analysis
            
        Returns:
            Optimized prompt ready for analysis
        """
        return await self.process(user_input)