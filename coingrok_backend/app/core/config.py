"""
Core configuration settings for CoinGrok Backend.

Manages environment variables, API keys, and application settings
with comprehensive validation at startup.
"""

import os
import re
import logging
from typing import List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    """
    Application settings with environment variable support and validation.
    
    Loads and validates configuration from environment variables,
    failing fast with clear errors on invalid configuration.
    """
    
    def __init__(self):
        # Test mode detection
        self.testing = os.getenv("TESTING", "0") == "1"
        
        # Application Info (configurable)
        self.app_name = os.getenv("APP_NAME", "CoinGrok Backend API")
        self.version = os.getenv("APP_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # API Keys (Required in production, safe defaults in testing)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.grok_api_key = os.getenv("GROK_API_KEY")
        
        if self.testing:
            # In testing mode, provide safe defaults for missing secrets
            if not self.openai_api_key:
                self.openai_api_key = "test-openai-key"
            if not self.grok_api_key:
                self.grok_api_key = "test-grok-key"
        
        # API Configuration (configurable)
        self.openai_api_url = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
        self.grok_api_url = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-5")
        self.grok_model = os.getenv("GROK_MODEL", "grok-4-0709")
        
        # Database Configuration
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./coingrok.db")
        
        # CORS Configuration
        cors_origins_str = os.getenv("CORS_ORIGINS")
        if not cors_origins_str and self.debug:
            cors_origins_str = "http://localhost:3000"  # Dev fallback only
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")] if cors_origins_str else []
        
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # Job Configuration
        try:
            self.job_cleanup_hours = int(os.getenv("JOB_CLEANUP_HOURS", "1"))
            self.max_user_input_length = int(os.getenv("MAX_USER_INPUT_LENGTH", "5000"))
        except ValueError as e:
            raise ValueError(f"Invalid numeric configuration: {e}")
        
        # HTTP Client Configuration - parse numerics with error handling
        self.http_timeout_seconds = self._parse_float("HTTP_TIMEOUT_SECONDS", "120")
        self.http_max_retries = self._parse_int("HTTP_MAX_RETRIES", "1")
        self.http_retry_backoff_base = self._parse_float("HTTP_RETRY_BACKOFF_BASE", "0.5")
        self.http_max_connections = self._parse_int("HTTP_MAX_CONNECTIONS", "100")
        self.http_max_keepalive = self._parse_int("HTTP_MAX_KEEPALIVE", "10")
        
        # Grok-specific timeout configuration
        self.grok_timeout_seconds = self._parse_float("GROK_TIMEOUT_SECONDS", "200")
        self.grok_connect_timeout = self._parse_float("GROK_CONNECT_TIMEOUT", "10.0")
        self.grok_write_timeout = self._parse_float("GROK_WRITE_TIMEOUT", "30.0")
        self.grok_pool_timeout = self._parse_float("GROK_POOL_TIMEOUT", "5.0")
        
        # Request Limits Configuration
        self.body_max_bytes = self._parse_int("BODY_MAX_BYTES", "1000000")  # ~1MB
        
        # Rate Limiting Configuration
        self.rate_limit_per_min = self._parse_int("RATE_LIMIT_PER_MIN", "60")
        self.rate_limit_burst = self._parse_int("RATE_LIMIT_BURST", "120")
        
        # IP-specific Rate Limiting Configuration  
        self.rate_limit_ip_per_min = self._parse_int("RATE_LIMIT_IP_PER_MIN", "300")
        self.rate_limit_ip_burst = self._parse_int("RATE_LIMIT_IP_BURST", "600")
        
        # Supabase Configuration
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_role = os.getenv("SUPABASE_SERVICE_ROLE")

        # JWT Configuration
        self.jwt_secret = os.getenv("JWT_SECRET")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")

        # Google OAuth
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        # Test-aware validation for additional required fields
        if self.testing:
            # In testing mode, provide safe defaults for missing configuration
            if not self.supabase_url:
                self.supabase_url = "https://test-project.supabase.co"
            if not self.supabase_anon_key:
                self.supabase_anon_key = "test-supabase-anon-key"
            if not self.supabase_service_role:
                self.supabase_service_role = "test-supabase-service-role"
            if not self.jwt_secret:
                self.jwt_secret = "test-jwt-secret"
            if not self.google_client_id:
                self.google_client_id = "test-client-id.apps.googleusercontent.com"
            if not self.google_client_secret:
                self.google_client_secret = "test-client-secret"
        
        # Run comprehensive validation unless in testing mode
        if not self.testing:
            self._validate_configuration()
    
    def _parse_int(self, env_var: str, default: str) -> int:
        """Parse integer from environment variable with descriptive error."""
        try:
            value = os.getenv(env_var, default)
            # Use default if environment variable is empty
            if not value or value.strip() == "":
                value = default
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid {env_var}: must be an integer, got '{os.getenv(env_var)}'")
    
    def _parse_float(self, env_var: str, default: str) -> float:
        """Parse float from environment variable with descriptive error."""
        try:
            value = os.getenv(env_var, default)
            # Use default if environment variable is empty
            if not value or value.strip() == "":
                value = default
            return float(value)
        except ValueError:
            raise ValueError(f"Invalid {env_var}: must be a number, got '{os.getenv(env_var)}'")
    
    def _validate_configuration(self) -> None:
        """
        Comprehensive configuration validation.
        
        Validates all configuration values and relationships,
        accumulating all errors and raising once with a complete list.
        
        Raises:
            ValueError: If any configuration is invalid
        """
        errors: List[str] = []
        
        # Validate required API keys
        if not self.openai_api_key or len(self.openai_api_key.strip()) < 10:
            errors.append("OPENAI_API_KEY is missing or too short (minimum 10 characters)")
        
        if not self.grok_api_key or len(self.grok_api_key.strip()) < 10:
            errors.append("GROK_API_KEY is missing or too short (minimum 10 characters)")
        
        # Validate URLs
        if not self._is_valid_url(self.openai_api_url):
            errors.append(f"OPENAI_API_URL is invalid: {self.openai_api_url}")
        
        if not self._is_valid_url(self.grok_api_url):
            errors.append(f"GROK_API_URL is invalid: {self.grok_api_url}")
        
        # Validate database URL format
        if not self._is_valid_database_url(self.database_url):
            errors.append(f"DATABASE_URL format is invalid: {self.database_url[:50]}...")
        
        # Validate CORS configuration
        if not self.debug:
            # Production mode: require explicit CORS origins, no wildcards
            if not self.cors_origins:
                errors.append("CORS_ORIGINS is required in production mode")
            else:
                for origin in self.cors_origins:
                    if not self._is_valid_origin(origin):
                        errors.append(f"Invalid CORS origin: {origin}")
                    if origin == "*":
                        errors.append("Wildcard (*) CORS origin is not allowed in production mode")
        else:
            # Debug mode: allow wildcards but validate format
            for origin in self.cors_origins:
                if not self._is_valid_origin(origin):
                    errors.append(f"Invalid CORS origin: {origin}")
        
        # Validate Google OAuth configuration
        if not self.google_client_id or not self.google_client_id.endswith('.apps.googleusercontent.com'):
            errors.append("GOOGLE_CLIENT_ID is missing or invalid format (must end with .apps.googleusercontent.com)")
        
        # Validate cross-dependencies
        if self.supabase_url and not self.supabase_anon_key:
            errors.append("SUPABASE_ANON_KEY is required when SUPABASE_URL is provided")
        
        # Validate numeric ranges
        if not (1 <= self.http_timeout_seconds <= 300):
            errors.append(f"HTTP_TIMEOUT_SECONDS must be 1-300, got: {self.http_timeout_seconds}")
        
        if not (1 <= self.http_max_connections <= 10000):
            errors.append(f"HTTP_MAX_CONNECTIONS must be 1-10000, got: {self.http_max_connections}")
        
        if not (1 <= self.http_max_keepalive <= 10000):
            errors.append(f"HTTP_MAX_KEEPALIVE must be 1-10000, got: {self.http_max_keepalive}")
        
        if not (1 <= self.rate_limit_per_min <= 10000):
            errors.append(f"RATE_LIMIT_PER_MIN must be 1-10000, got: {self.rate_limit_per_min}")
        
        if not (1 <= self.rate_limit_burst <= 20000):
            errors.append(f"RATE_LIMIT_BURST must be 1-20000, got: {self.rate_limit_burst}")
        
        if self.rate_limit_burst < self.rate_limit_per_min:
            errors.append(f"RATE_LIMIT_BURST ({self.rate_limit_burst}) must be >= RATE_LIMIT_PER_MIN ({self.rate_limit_per_min})")
        
        if not (0.1 <= self.grok_connect_timeout <= 60):
            errors.append(f"GROK_CONNECT_TIMEOUT must be 0.1-60, got: {self.grok_connect_timeout}")
        
        if not (0.1 <= self.grok_write_timeout <= 120):
            errors.append(f"GROK_WRITE_TIMEOUT must be 0.1-120, got: {self.grok_write_timeout}")
        
        if not (0.1 <= self.grok_pool_timeout <= 30):
            errors.append(f"GROK_POOL_TIMEOUT must be 0.1-30, got: {self.grok_pool_timeout}")
        
        # Validate model names are not empty
        if not self.openai_model or not self.openai_model.strip():
            errors.append("OPENAI_MODEL cannot be empty")
        
        if not self.grok_model or not self.grok_model.strip():
            errors.append("GROK_MODEL cannot be empty")
        
        # Warn about logical consistency (but don't fail)
        total_grok_timeout = self.grok_connect_timeout + self.grok_write_timeout + self.grok_timeout_seconds
        if total_grok_timeout > self.http_timeout_seconds:
            logger.warning(
                f"Sum of Grok timeouts ({total_grok_timeout}s) exceeds HTTP_TIMEOUT_SECONDS ({self.http_timeout_seconds}s). "
                "This may cause unexpected behavior."
            )
        
        # Raise with all errors if any found
        if errors:
            raise ValueError(
                "Configuration validation failed:\n" + 
                "\n".join(f"  - {error}" for error in errors)
            )
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            bool: True if URL is valid, False otherwise
        """
        if not url:
            return False
        
        # Simple URL validation pattern
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        return bool(url_pattern.match(url))
    
    def _is_valid_database_url(self, url: str) -> bool:
        """
        Validate database URL format.
        
        Args:
            url: Database URL string to validate
            
        Returns:
            bool: True if database URL is valid, False otherwise
        """
        if not url:
            return False
        
        # Accept common database URL schemes
        valid_schemes = (
            'postgresql://',
            'postgresql+psycopg://',
            'postgresql+psycopg2://',
            'sqlite:///',
            'mysql://',
            'mysql+pymysql://'
        )
        return any(url.startswith(scheme) for scheme in valid_schemes)
    
    def _is_valid_origin(self, origin: str) -> bool:
        """
        Validate CORS origin format.
        
        Args:
            origin: CORS origin string to validate
            
        Returns:
            bool: True if origin is valid, False otherwise
        """
        if not origin:
            return False
        
        # Allow wildcard only in debug mode
        if origin == "*":
            return self.debug
        
        # Must start with http:// or https://
        return origin.startswith(('http://', 'https://'))
    
    @property
    def connect_args(self) -> dict:
        """Get database connection arguments based on database type."""
        if self.database_url.startswith("sqlite"):
            return {"check_same_thread": False}
        return {}
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_url.startswith("sqlite")


# Global settings instance
settings = Settings()