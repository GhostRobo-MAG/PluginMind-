"""
Logging configuration for PluginMind Backend.

Provides centralized logging setup with structured formatting and correlation ID support.
"""

import json
import logging
import re
import sys
from datetime import datetime
from typing import Mapping, Any
from app.core.config import settings


# Sensitive header keys that should be redacted in logs
SENSITIVE_HEADER_KEYS = {"authorization", "proxy-authorization", "x-api-key", "api-key"}


def redact_headers(headers: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Redact sensitive header values for safe logging.
    
    Args:
        headers: Dictionary of HTTP headers
        
    Returns:
        Dictionary with sensitive values redacted
    """
    safe_headers = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADER_KEYS:
            safe_headers[key] = "***REDACTED***"
        else:
            safe_headers[key] = value
    return safe_headers


class StructuredJsonFormatter(logging.Formatter):
    """JSON structured log formatter with correlation ID support."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            str: JSON formatted log entry
        """
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, 'request_id', '-'),
            "route": getattr(record, 'route', None),
            "user_id": getattr(record, 'user_id', None)
        }
        
        # Remove null/None values for cleaner JSON
        log_entry = {k: v for k, v in log_entry.items() if v is not None}
        
        return json.dumps(log_entry)


class SecretRedactionFilter(logging.Filter):
    """Filter to redact sensitive information from logs."""
    
    REDACTION_PATTERNS = [
        # API key patterns (api_key=value, "api_key": "value")
        (re.compile(r'(api_key["\']?\s*[=:]\s*["\']?)([^"\'&\s]+)', re.IGNORECASE), r'\1[REDACTED]'),
        # Bearer tokens
        (re.compile(r'(bearer\s+)([a-zA-Z0-9\-._~+/]+=*)', re.IGNORECASE), r'\1[REDACTED]'),
        # OpenAI API keys (sk-...)
        (re.compile(r'(sk-[a-zA-Z0-9]{32,})', re.IGNORECASE), '[API_KEY_REDACTED]'),
        # JWT tokens (eyJ...)
        (re.compile(r'(eyJ[a-zA-Z0-9\-._~+/=]+)', re.IGNORECASE), '[JWT_REDACTED]'),
        # Generic secret patterns
        (re.compile(r'(secret["\']?\s*[=:]\s*["\']?)([^"\'&\s]+)', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(password["\']?\s*[=:]\s*["\']?)([^"\'&\s]+)', re.IGNORECASE), r'\1[REDACTED]'),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Redact sensitive information from log messages.
        
        Args:
            record: Log record to filter
            
        Returns:
            bool: Always True (don't filter out records)
        """
        # Apply redaction to the message
        if hasattr(record, 'msg'):
            message = str(record.msg)
            for pattern, replacement in self.REDACTION_PATTERNS:
                message = pattern.sub(replacement, message)
            record.msg = message
        
        # Also redact any args that might contain sensitive data
        if hasattr(record, 'args') and record.args:
            redacted_args = []
            for arg in record.args:
                arg_str = str(arg)
                for pattern, replacement in self.REDACTION_PATTERNS:
                    arg_str = pattern.sub(replacement, arg_str)
                redacted_args.append(arg_str if isinstance(arg, str) else arg)
            record.args = tuple(redacted_args)
        
        return True


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter to inject correlation ID and user ID into log records.
    
    Adds request_id and user_id fields to log records for structured logging
    and request tracing capabilities.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add request_id and user_id to log record.
        
        Args:
            record: Log record to modify
            
        Returns:
            bool: Always True (don't filter out records)
        """
        # Import here to avoid circular imports
        try:
            from app.middleware.correlation_id import get_request_id, get_request_route
            record.request_id = get_request_id()
            record.route = get_request_route()
        except ImportError:
            # Fallback if middleware not yet imported
            record.request_id = "-"
            record.route = None
        
        # Try to extract user_id from request context
        # For now, user_id extraction is handled at the route level
        # Individual route handlers can set record.user_id manually if needed
        # Future enhancement: implement user context variable similar to request_id_context
        pass
        
        return True


def setup_logging() -> None:
    """
    Configure application logging with structured format and correlation ID support.
    
    Sets up console logging with appropriate formatting, level, and request ID
    injection based on application settings. Uses JSON formatting for production
    and text formatting for debug mode.
    """
    # Create handler 
    handler = logging.StreamHandler(sys.stdout)
    
    # Add filters
    handler.addFilter(CorrelationIdFilter())
    handler.addFilter(SecretRedactionFilter())
    
    # Choose formatter based on log level
    if settings.log_level.upper() == 'DEBUG':
        # Use text format for local development/debugging
        enhanced_format = settings.log_format + " - request_id=%(request_id)s - route=%(route)s"
        formatter = logging.Formatter(enhanced_format)
    else:
        # Use JSON format for production
        formatter = StructuredJsonFormatter()
    
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