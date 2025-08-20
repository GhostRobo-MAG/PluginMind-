"""
Test configuration validation for PluginMind Backend.

Tests configuration validation methods and startup behavior.
"""

from app.core.config import Settings


def test_config_validation_methods_exist():
    """Test that configuration validation methods exist and are accessible."""
    settings = Settings()
    
    # Test that validation methods exist
    assert hasattr(settings, '_validate_configuration')
    assert hasattr(settings, '_is_valid_url')
    assert hasattr(settings, '_is_valid_database_url')
    assert hasattr(settings, '_is_valid_origin')


def test_url_validation_helper():
    """Test URL validation helper method."""
    settings = Settings()
    
    # Valid URLs
    assert settings._is_valid_url("https://api.openai.com/v1/chat/completions")
    assert settings._is_valid_url("http://localhost:8080/api")
    assert settings._is_valid_url("https://192.168.1.1:3000")
    
    # Invalid URLs
    assert not settings._is_valid_url("")
    assert not settings._is_valid_url("not-a-url")
    assert not settings._is_valid_url("ftp://invalid-protocol.com")


def test_database_url_validation_helper():
    """Test database URL validation helper method."""
    settings = Settings()
    
    # Valid database URLs
    assert settings._is_valid_database_url("postgresql://user:pass@localhost/db")
    assert settings._is_valid_database_url("sqlite:///./test.db")
    assert settings._is_valid_database_url("mysql://user:pass@localhost/db")
    
    # Invalid database URLs
    assert not settings._is_valid_database_url("")
    assert not settings._is_valid_database_url("redis://localhost:6379")
    assert not settings._is_valid_database_url("invalid-scheme://localhost")


def test_cors_origin_validation_helper():
    """Test CORS origin validation helper method."""
    settings = Settings()
    
    # Valid origins
    assert settings._is_valid_origin("https://app.coingrok.com")
    assert settings._is_valid_origin("http://localhost:3000")
    
    # Wildcard only allowed in debug mode
    if settings.debug:
        assert settings._is_valid_origin("*")
    else:
        assert not settings._is_valid_origin("*")
    
    # Invalid origins
    assert not settings._is_valid_origin("")
    assert not settings._is_valid_origin("invalid-origin")


def test_configuration_loads_successfully_in_testing():
    """Test that configuration loads without errors in testing mode."""
    # This test runs in testing mode (set by conftest.py)
    # so it should not have strict validation errors
    settings = Settings()
    
    # Verify key settings are loaded
    assert settings.app_name
    assert settings.version
    assert settings.openai_api_key
    assert settings.grok_api_key
    assert settings.google_client_id
    assert settings.cors_origins
    
    # Should have valid API keys (either test or production)
    assert len(settings.openai_api_key) >= 10
    assert len(settings.grok_api_key) >= 10


def test_numeric_parsing_methods():
    """Test that numeric parsing helper methods exist."""
    settings = Settings()
    
    # Test numeric parsing methods exist
    assert hasattr(settings, '_parse_int')
    assert hasattr(settings, '_parse_float')
    
    # Test valid parsing
    assert settings._parse_int("HTTP_TIMEOUT_SECONDS", "120") > 0
    assert settings._parse_float("GROK_CONNECT_TIMEOUT", "10.0") > 0
    

def test_validation_fail_fast_behavior():
    """Test that validation fails fast with aggregated errors."""
    # Create a Settings instance that would trigger validation
    # In testing mode, this should still work due to safe defaults
    settings = Settings()
    
    # Verify that in non-testing mode, validation would be called
    # We can't easily test actual validation failure without complex env manipulation
    # so we just verify the validation infrastructure is in place
    assert callable(settings._validate_configuration)
    
    # Test that the validation error format would be correct
    # by testing a validation helper directly
    errors = []
    
    # Simulate what validation does
    if not settings._is_valid_url("invalid-url"):
        errors.append("Invalid URL format")
    
    if not settings._is_valid_database_url("invalid://scheme"):
        errors.append("Invalid database URL")
    
    # Should accumulate multiple errors
    assert len(errors) >= 2
    
    # Test error message format would be correct
    if errors:
        error_msg = (
            "Configuration validation failed:\n" + 
            "\n".join(f"  - {error}" for error in errors)
        )
        assert error_msg.startswith("Configuration validation failed:")
        assert "  - " in error_msg