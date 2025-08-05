"""
Custom exception classes for CoinGrok Backend.

Defines application-specific exceptions for better error handling
and user experience.
"""


class CoinGrokBaseException(Exception):
    """Base exception for all CoinGrok-specific errors."""
    pass


class APIKeyMissingError(CoinGrokBaseException):
    """Raised when required API keys are missing."""
    pass


class AIServiceError(CoinGrokBaseException):
    """Raised when AI service (OpenAI/Grok) requests fail."""
    pass


class RateLimitError(AIServiceError):
    """Raised when API rate limits are exceeded."""
    pass


class InvalidInputError(CoinGrokBaseException):
    """Raised when user input validation fails."""
    pass


class JobNotFoundError(CoinGrokBaseException):
    """Raised when requested job ID doesn't exist."""
    pass


class DatabaseError(CoinGrokBaseException):
    """Raised when database operations fail."""
    pass