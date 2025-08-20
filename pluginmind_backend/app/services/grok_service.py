"""
Grok service implementation with AIService interface.

Handles all interactions with Grok (xAI) API for the final analysis
step of the 4-D Prompt Engine (Deliver phase).
"""

import json
import uuid
from typing import Optional, Dict, Any
import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging import get_logger, redact_headers
from app.core.exceptions import AIServiceError, RateLimitError, ServiceUnavailableError
from app.utils.http import http_client
from app.services.ai_service_interface import (
    AIService,
    AIServiceMetadata,
    AIServiceCapability
)

logger = get_logger(__name__)


class GrokService(AIService):
    """
    Grok service implementation with plugin interface.
    
    Handles crypto market analysis using Grok's AI capabilities.
    Provides resilient HTTP calls with retries, timeouts, and error handling.
    """
    
    def __init__(self):
        """Initialize Grok service with configuration."""
        self.api_url = settings.grok_api_url
        self.model = settings.grok_model
        self.api_key = settings.grok_api_key
        
        # Grok-specific timeout configuration
        self.timeout_config = httpx.Timeout(
            connect=settings.grok_connect_timeout,
            read=settings.grok_timeout_seconds,
            write=settings.grok_write_timeout,
            pool=settings.grok_pool_timeout
        )
        
        # Service metadata
        self._metadata = AIServiceMetadata(
            name="Grok AI Service",
            provider="xAI",
            version="1.0.0",
            capabilities=[
                AIServiceCapability.GENERIC_ANALYSIS,
                AIServiceCapability.DOCUMENT_SUMMARIZATION,
                AIServiceCapability.DOCUMENT_ANALYSIS,
                AIServiceCapability.CRYPTO_ANALYSIS,
                AIServiceCapability.SENTIMENT_ANALYSIS,
                AIServiceCapability.MARKET_PREDICTION,
                AIServiceCapability.NEWS_SUMMARIZATION
            ],
            model=self.model,
            max_tokens=3000,
            temperature=0.8
        )
        
        logger.info(
            f"Grok service initialized (model: {self.model}, "
            f"capabilities: {[c.value for c in self._metadata.capabilities]})"
        )
    
    def get_metadata(self) -> AIServiceMetadata:
        """
        Get metadata about this Grok service.
        
        Returns:
            AIServiceMetadata describing the service
        """
        return self._metadata
    
    async def health_check(self) -> bool:
        """
        Check if Grok service is healthy and available.
        
        Performs a minimal API call to verify connectivity and authentication.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Simple health check with minimal tokens
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "ping"}
                ],
                "max_tokens": 5
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            response = await http_client.request_with_retries(
                method="POST",
                url=self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout_config
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"Grok health check failed: {str(e)}")
            return False
    
    async def validate_input(self, input_text: str) -> bool:
        """
        Validate input for Grok analysis.
        
        Args:
            input_text: Optimized prompt to validate
            
        Returns:
            True if input is valid for processing
        """
        if not input_text or not input_text.strip():
            return False
        
        # Grok expects well-structured prompts
        # Check for minimum meaningful content
        if len(input_text) < 10:
            logger.warning(f"Input too short for meaningful analysis: {len(input_text)}")
            return False
        
        return True
    
    async def prepare_request(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare Grok API request payload.
        
        Args:
            input_text: Optimized prompt for analysis
            **kwargs: Additional parameters (system_prompt, temperature, etc.)
            
        Returns:
            Prepared request payload for Grok API
        """
        system_prompt = kwargs.get(
            "system_prompt", 
            "You are an AI crypto analyst with real-time market insights."
        )
        temperature = kwargs.get("temperature", self._metadata.temperature)
        max_tokens = kwargs.get("max_tokens", self._metadata.max_tokens)
        
        # Add any Grok-specific parameters
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Grok may support additional parameters for crypto analysis
        if kwargs.get("include_sentiment", True):
            payload["include_sentiment"] = True
        
        if kwargs.get("include_market_data", True):
            payload["include_market_data"] = True
        
        return payload
    
    async def process(self, input_text: str, **kwargs) -> str:
        """
        Process optimized prompt through Grok for crypto analysis.
        
        Takes an optimized prompt and generates comprehensive crypto
        analysis including sentiment, news, market data, and recommendations.
        
        Args:
            input_text: Pre-optimized prompt from prompt optimizer
            **kwargs: Additional parameters (system_prompt, include_sentiment, etc.)
            
        Returns:
            Comprehensive crypto analysis result
            
        Raises:
            AIServiceError: For invalid responses or business logic errors
            ServiceUnavailableError: For service failures
        """
        # Validate input
        if not await self.validate_input(input_text):
            raise AIServiceError("Invalid input for Grok processing")
        
        request_id = str(uuid.uuid4())[:8]
        
        try:
            logger.info(
                f"Sending optimized prompt to Grok for analysis "
                f"(request_id={request_id})"
            )
            
            # Prepare request payload
            payload = await self.prepare_request(input_text, **kwargs)
            
            # Make API request with Grok-specific timeout
            response_data = await self._request_with_retries(payload, request_id)
            
            # Extract and validate response
            analysis_result = self._extract_response(response_data, request_id)
            
            # Post-process if needed (e.g., format crypto data)
            if kwargs.get("format_output", False):
                analysis_result = self._format_crypto_analysis(analysis_result)
            
            logger.info(
                f"Successfully received analysis from Grok (request_id={request_id})"
            )
            
            return analysis_result
            
        except HTTPException:
            # Re-raise HTTP exceptions (already logged in retry logic)
            raise
        except AIServiceError:
            # Re-raise business logic errors
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in Grok analysis (request_id={request_id}): {str(e)}"
            )
            raise ServiceUnavailableError("Grok service unavailable")
    
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
                json=payload,
                timeout=self.timeout_config
            )
            
            return response.json()
            
        except HTTPException:
            # Re-raise HTTP exceptions from retry logic
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in Grok request (request_id={request_id}): {str(e)}"
            )
            raise ServiceUnavailableError("Grok service unavailable")
    
    def _extract_response(self, response_data: dict, request_id: str) -> str:
        """
        Extract and validate the response from Grok API.
        
        Args:
            response_data: Raw API response
            request_id: Request correlation ID
            
        Returns:
            Extracted analysis content
            
        Raises:
            AIServiceError: If response is invalid
        """
        # Validate response structure
        if not response_data.get("choices"):
            logger.error(f"Invalid Grok response: no choices (request_id={request_id})")
            raise AIServiceError("Invalid response from Grok: no choices")
        
        if not response_data["choices"][0].get("message"):
            logger.error(f"Invalid Grok response: no message (request_id={request_id})")
            raise AIServiceError("Invalid response from Grok: no message")
        
        content = response_data["choices"][0]["message"].get("content")
        if not content:
            logger.error(f"Invalid Grok response: empty content (request_id={request_id})")
            raise AIServiceError("Empty response from Grok")
        
        return content.strip()
    
    def _format_crypto_analysis(self, raw_analysis: str) -> str:
        """
        Format crypto analysis output for better readability.
        
        Args:
            raw_analysis: Raw analysis text from Grok
            
        Returns:
            Formatted analysis with structured sections
        """
        # This is a placeholder for formatting logic
        # In production, this could parse and restructure the analysis
        # into consistent sections like sentiment, news, recommendations, etc.
        
        formatted = f"""
=== CRYPTO ANALYSIS REPORT ===

{raw_analysis}

=== END OF REPORT ===
        """.strip()
        
        return formatted
    
    # Backward compatibility method
    async def analyze(self, optimized_prompt: str) -> str:
        """
        Legacy method for crypto analysis.
        
        Maintained for backward compatibility with existing code.
        Delegates to the process() method.
        
        Args:
            optimized_prompt: Pre-optimized prompt from OpenAI service
            
        Returns:
            Comprehensive crypto analysis result
        """
        return await self.process(optimized_prompt)