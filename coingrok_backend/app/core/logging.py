"""
Logging configuration for CoinGrok Backend.

Provides centralized logging setup with structured formatting and correlation ID support.
"""

import logging
import sys
from app.core.config import settings


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter to inject correlation ID into log records.
    
    Adds request_id field to log records for structured logging
    and request tracing capabilities.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add request_id to log record.
        
        Args:
            record: Log record to modify
            
        Returns:
            bool: Always True (don't filter out records)
        """
        # Import here to avoid circular imports
        try:
            from app.middleware.correlation_id import get_request_id
            record.request_id = get_request_id()
        except ImportError:
            # Fallback if middleware not yet imported
            record.request_id = "-"
        
        return True


def setup_logging() -> None:
    """
    Configure application logging with structured format and correlation ID support.
    
    Sets up console logging with appropriate formatting, level, and request ID
    injection based on application settings.
    """
    # Create handler with correlation ID filter
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(CorrelationIdFilter())
    
    # Enhanced format with request_id field
    enhanced_format = settings.log_format + " - request_id=%(request_id)s"
    formatter = logging.Formatter(enhanced_format)
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.handlers.clear()  # Remove any existing handlers
    root_logger.addHandler(handler)
    
    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)