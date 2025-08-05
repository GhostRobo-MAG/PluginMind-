"""
OpenAI service for prompt optimization.

Handles all interactions with OpenAI's API for the 4-D Prompt Engine's
optimization step (Deconstruct → Diagnose → Develop).
"""

from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import AIServiceError, RateLimitError
from app.ash_prompt import ASH_SYSTEM_PROMPT

logger = get_logger(__name__)


class OpenAIService:
    """
    Service class for OpenAI API interactions.
    
    Handles prompt optimization using GPT-4 as part of the 4-D Prompt Engine.
    Provides error handling and logging for all OpenAI operations.
    """
    
    def __init__(self):
        """Initialize OpenAI client with API key from settings."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        logger.info("OpenAI service initialized")
    
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
            RateLimitError: When OpenAI rate limits are exceeded
            AIServiceError: For other OpenAI API errors
        """
        try:
            logger.info(f"Optimizing prompt for input length: {len(user_input)}")
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": ASH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_input},
                ],
            )
            
            # Validate response
            if not response.choices or not response.choices[0].message.content:
                raise AIServiceError("Empty or invalid response from OpenAI")
            
            optimized_prompt = response.choices[0].message.content.strip()
            logger.info("Successfully optimized prompt via OpenAI")
            
            return optimized_prompt
            
        except Exception as e:
            error_message = str(e).lower()
            
            if "rate limit" in error_message:
                logger.warning("OpenAI rate limit exceeded")
                raise RateLimitError("Rate limit exceeded. Please try again later.")
            elif "api key" in error_message or "unauthorized" in error_message:
                logger.error("OpenAI authentication failed")
                raise AIServiceError("API authentication failed")
            elif "timeout" in error_message:
                logger.warning("OpenAI request timeout")
                raise AIServiceError("Request timeout. Please try again.")
            else:
                logger.error(f"OpenAI service error: {str(e)}")
                raise AIServiceError(f"OpenAI service failed: {str(e)}")


# Global service instance
openai_service = OpenAIService()