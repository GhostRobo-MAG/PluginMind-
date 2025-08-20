"""
Custom exception classes for PluginMind Backend.

Defines application-specific exceptions for better error handling
and user experience.
"""


class PluginMindBaseException(Exception):
    """Base exception for all PluginMind-specific errors."""
    pass


class APIKeyMissingError(PluginMindBaseException):
    """Raised when required API keys are missing."""
    pass


class AIServiceError(PluginMindBaseException):
    """Raised when AI service (OpenAI/Grok) requests fail."""
    pass


class RateLimitError(AIServiceError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: int = None):
        """
        Initialize RateLimitError with optional retry-after value.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying (optional)
        """
        super().__init__(message)
        self.retry_after = retry_after


class InvalidInputError(PluginMindBaseException):
    """Raised when user input validation fails."""
    pass


class JobNotFoundError(PluginMindBaseException):
    """Raised when requested job ID doesn't exist."""
    pass


class DatabaseError(PluginMindBaseException):
    """Raised when database operations fail."""
    pass


class AuthenticationError(PluginMindBaseException):
    """Raised when authentication fails."""
    pass


class UserAccessError(PluginMindBaseException):
    """Raised when user account operations fail."""
    pass


class QueryLimitExceededError(PluginMindBaseException):
    """Raised when user exceeds query limits."""
    pass


class UserNotFoundError(PluginMindBaseException):
    """Raised when requested user doesn't exist."""
    pass


class ServiceUnavailableError(PluginMindBaseException):
    """Raised when external services are unavailable."""
    pass


# Error code constants
class ErrorCodes:
    """Constants for error codes used in API responses."""
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_TOKEN = "INVALID_TOKEN"
    USER_ACCESS_FAILED = "USER_ACCESS_FAILED"
    QUERY_LIMIT_EXCEEDED = "QUERY_LIMIT_EXCEEDED"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    INVALID_INPUT = "INVALID_INPUT"
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    DATABASE_ERROR = "DATABASE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    REQUEST_TOO_LARGE = "REQUEST_TOO_LARGE"