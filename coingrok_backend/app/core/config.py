"""
Core configuration settings for CoinGrok Backend.

Manages environment variables, API keys, and application settings
with simple environment variable loading.
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Application settings with environment variable support.
    
    Simple configuration class that loads settings from environment variables.
    """
    
    def __init__(self):
        # Application Info
        self.app_name = "CoinGrok Backend API"
        self.version = "1.0.0"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # API Keys (Required)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.grok_api_key = os.getenv("GROK_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not self.grok_api_key:
            raise ValueError("GROK_API_KEY environment variable is required")
        
        # API Configuration
        self.grok_api_url = "https://api.x.ai/v1/chat/completions"
        self.openai_model = "gpt-5"
        self.grok_model = "grok-4-latest"
        
        # Database Configuration
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./coingrok.db")
        
        # CORS Configuration
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # Job Configuration
        self.job_cleanup_hours = int(os.getenv("JOB_CLEANUP_HOURS", "1"))
        self.max_user_input_length = int(os.getenv("MAX_USER_INPUT_LENGTH", "5000"))
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

        # Validation
        if not all([self.supabase_url, self.supabase_anon_key]):
            raise ValueError("Missing required Supabase configuration")
        if not self.google_client_id:
            raise ValueError("Missing required Google OAuth configuration")
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