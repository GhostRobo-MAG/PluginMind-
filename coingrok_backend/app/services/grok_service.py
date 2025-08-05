"""
Grok service for crypto analysis.

Handles all interactions with Grok (xAI) API for the final analysis
step of the 4-D Prompt Engine (Deliver phase).
"""

from xai_sdk import AsyncClient
from xai_sdk.chat import user, system
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import AIServiceError, RateLimitError

logger = get_logger(__name__)


class GrokService:
    """
    Service class for Grok (xAI) API interactions.
    
    Handles crypto market analysis using Grok's AI capabilities.
    Provides comprehensive error handling and logging.
    """
    
    def __init__(self):
        """Initialize Grok client with API key from settings."""
        self.client = AsyncClient(api_key=settings.grok_api_key)
        logger.info("Grok service initialized")
    
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
            RateLimitError: When Grok rate limits are exceeded
            AIServiceError: For other Grok API errors
        """
        try:
            logger.info("Sending optimized prompt to Grok for analysis")
            
            # Create chat session with Grok
            chat = self.client.chat.create(model=settings.grok_model)
            chat.append(system("You are an AI crypto analyst."))
            chat.append(user(optimized_prompt))
            
            # Get analysis response
            response = await chat.sample()
            
            # Validate response
            if not hasattr(response, "content") or not response.content:
                raise AIServiceError("Empty or invalid response from Grok")
            
            analysis_result = response.content
            logger.info("Successfully received analysis from Grok")
            
            return analysis_result
            
        except Exception as e:
            error_message = str(e).lower()
            
            if "rate limit" in error_message:
                logger.warning("Grok rate limit exceeded")
                raise RateLimitError("Rate limit exceeded. Please try again later.")
            elif "api key" in error_message or "unauthorized" in error_message:
                logger.error("Grok authentication failed")
                raise AIServiceError("API authentication failed")
            elif "timeout" in error_message:
                logger.warning("Grok request timeout")
                raise AIServiceError("Request timeout. Please try again.")
            else:
                logger.error(f"Grok service error: {str(e)}")
                raise AIServiceError(f"Grok service failed: {str(e)}")


# Global service instance
grok_service = GrokService()