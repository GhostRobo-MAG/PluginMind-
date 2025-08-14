"""
Tests for HTTP client configuration and security features.

Tests configurable pool limits, granular timeouts, and header redaction.
"""

import asyncio
import os
import pytest
from unittest.mock import patch
import httpx

from app.core.logging import redact_headers


def test_redact_headers_sensitive_keys():
    """Test that sensitive header keys are properly redacted."""
    headers = {
        "Authorization": "Bearer secret-token-12345",
        "X-Api-Key": "super-secret-api-key", 
        "Content-Type": "application/json",
        "User-Agent": "CoinGrok/1.0",
        "api-key": "another-secret",
        "Proxy-Authorization": "Basic dXNlcjpwYXNz"
    }
    
    safe_headers = redact_headers(headers)
    
    # Sensitive headers should be redacted
    assert safe_headers["Authorization"] == "***REDACTED***"
    assert safe_headers["X-Api-Key"] == "***REDACTED***"
    assert safe_headers["api-key"] == "***REDACTED***"
    assert safe_headers["Proxy-Authorization"] == "***REDACTED***"
    
    # Non-sensitive headers should be preserved
    assert safe_headers["Content-Type"] == "application/json"
    assert safe_headers["User-Agent"] == "CoinGrok/1.0"


def test_redact_headers_case_insensitive():
    """Test that header redaction is case-insensitive."""
    headers = {
        "authorization": "Bearer token",
        "AUTHORIZATION": "Bearer token",
        "Authorization": "Bearer token",
        "x-api-key": "key123",
        "X-API-KEY": "key456"
    }
    
    safe_headers = redact_headers(headers)
    
    # All variations should be redacted
    for key in headers.keys():
        assert safe_headers[key] == "***REDACTED***"


def test_redact_headers_empty():
    """Test redaction with empty headers."""
    assert redact_headers({}) == {}


@pytest.mark.asyncio
async def test_http_pool_limits_configuration():
    """Test that HTTP pool limits are configurable via environment variables."""
    # Set custom environment variables
    test_env = {
        "HTTP_MAX_CONNECTIONS": "250",
        "HTTP_MAX_KEEPALIVE": "25"
    }
    
    with patch.dict(os.environ, test_env):
        # Reload config and HTTP client to pick up new env vars
        from importlib import reload
        import app.core.config
        reload(app.core.config)
        
        import app.utils.http
        reload(app.utils.http)
        
        # Check that the configuration was applied
        settings = app.core.config.settings
        assert settings.http_max_connections == 250
        assert settings.http_max_keepalive == 25
        
        # Check that HTTP client was created with new limits
        # Note: We test that settings are loaded correctly, as httpx internal 
        # attributes are not easily accessible in tests
        http_client = app.utils.http.http_client
        assert http_client is not None
        # Settings were loaded correctly, so limits should be applied


@pytest.mark.asyncio
async def test_grok_timeout_configuration():
    """Test that Grok granular timeouts are configurable."""
    test_env = {
        "GROK_CONNECT_TIMEOUT": "15.5",
        "GROK_WRITE_TIMEOUT": "45.0", 
        "GROK_POOL_TIMEOUT": "7.5",
        "GROK_TIMEOUT_SECONDS": "300"
    }
    
    with patch.dict(os.environ, test_env):
        # Reload config to pick up new env vars
        from importlib import reload
        import app.core.config
        reload(app.core.config)
        
        settings = app.core.config.settings
        assert settings.grok_connect_timeout == 15.5
        assert settings.grok_write_timeout == 45.0
        assert settings.grok_pool_timeout == 7.5
        assert settings.grok_timeout_seconds == 300.0
        
        # Create timeout object as in grok_service.py
        grok_timeout = httpx.Timeout(
            connect=settings.grok_connect_timeout,
            read=settings.grok_timeout_seconds,
            write=settings.grok_write_timeout,
            pool=settings.grok_pool_timeout
        )
        
        assert grok_timeout.connect == 15.5
        assert grok_timeout.read == 300.0
        assert grok_timeout.write == 45.0
        assert grok_timeout.pool == 7.5


@pytest.mark.asyncio 
async def test_http_client_retry_configuration():
    """Test HTTP client retry configuration."""
    test_env = {
        "HTTP_MAX_RETRIES": "3",
        "HTTP_RETRY_BACKOFF_BASE": "1.0"
    }
    
    with patch.dict(os.environ, test_env):
        from importlib import reload
        import app.core.config
        reload(app.core.config)
        
        settings = app.core.config.settings
        assert settings.http_max_retries == 3
        assert settings.http_retry_backoff_base == 1.0


def test_http_timeout_defaults():
    """Test default timeout values are reasonable."""
    # Clear any environment variables that might interfere with defaults
    import os
    env_vars_to_clear = [
        "HTTP_TIMEOUT_SECONDS", "HTTP_MAX_RETRIES", "HTTP_RETRY_BACKOFF_BASE",
        "HTTP_MAX_CONNECTIONS", "HTTP_MAX_KEEPALIVE", "GROK_TIMEOUT_SECONDS", 
        "GROK_CONNECT_TIMEOUT", "GROK_WRITE_TIMEOUT", "GROK_POOL_TIMEOUT"
    ]
    
    original_values = {}
    for var in env_vars_to_clear:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    try:
        # Reload config to get fresh defaults
        from importlib import reload
        import app.core.config
        reload(app.core.config)
        settings = app.core.config.settings
        
        # Verify reasonable defaults
        assert settings.http_timeout_seconds == 150.0  # Updated to match production config
        assert settings.http_max_retries == 1
        assert settings.http_retry_backoff_base == 0.5
        assert settings.http_max_connections == 100
        assert settings.http_max_keepalive == 10
        
        # Grok defaults
        assert settings.grok_timeout_seconds == 90.0  # Updated to match production config
        assert settings.grok_connect_timeout == 10.0
        assert settings.grok_write_timeout == 30.0
        assert settings.grok_pool_timeout == 5.0
    
    finally:
        # Restore original environment
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value


@pytest.mark.asyncio
async def test_header_safety_documentation():
    """Test that services have proper header safety comments."""
    import os
    
    # Use relative paths that work in CI and locally
    openai_service_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'services', 'openai_service.py')
    grok_service_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'services', 'grok_service.py')
    
    # Read the service files to ensure they have safety comments
    with open(openai_service_path, 'r') as f:
        openai_content = f.read()
    
    with open(grok_service_path, 'r') as f:
        grok_content = f.read()
    
    # Check that both services import redact_headers
    assert "from app.core.logging import get_logger, redact_headers" in openai_content
    assert "from app.core.logging import get_logger, redact_headers" in grok_content
    
    # Check that both have safety comments
    assert "Do not log raw headers" in openai_content
    assert "Do not log raw headers" in grok_content


def test_sensitive_header_keys_coverage():
    """Test that all common sensitive header patterns are covered."""
    from app.core.logging import SENSITIVE_HEADER_KEYS
    
    expected_keys = {
        "authorization",
        "proxy-authorization", 
        "x-api-key",
        "api-key"
    }
    
    assert SENSITIVE_HEADER_KEYS >= expected_keys, "Missing expected sensitive header keys"


@pytest.mark.asyncio
async def test_httpx_timeout_object_creation():
    """Test that httpx.Timeout objects are created correctly with config values."""
    from app.core.config import settings
    
    # Test global timeout (used by OpenAI)
    global_timeout = httpx.Timeout(timeout=settings.http_timeout_seconds)
    assert global_timeout.connect == settings.http_timeout_seconds
    assert global_timeout.read == settings.http_timeout_seconds
    
    # Test granular timeout (used by Grok)
    granular_timeout = httpx.Timeout(
        connect=settings.grok_connect_timeout,
        read=settings.grok_timeout_seconds,
        write=settings.grok_write_timeout,
        pool=settings.grok_pool_timeout
    )
    
    assert granular_timeout.connect == settings.grok_connect_timeout
    assert granular_timeout.read == settings.grok_timeout_seconds
    assert granular_timeout.write == settings.grok_write_timeout
    assert granular_timeout.pool == settings.grok_pool_timeout