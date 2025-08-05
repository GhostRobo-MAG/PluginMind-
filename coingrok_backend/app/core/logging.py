"""
Logging configuration for CoinGrok Backend.

Provides centralized logging setup with structured formatting.
"""

import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Configure application logging with structured format.
    
    Sets up console logging with appropriate formatting and level
    based on application settings.
    """
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
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