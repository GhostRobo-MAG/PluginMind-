"""
Test configuration for PluginMind Backend.

Sets up test environment with TESTING=1 flag and safe dummy environment variables
so that local pytest runs work out of the box without requiring real secrets.
"""

import os
import pytest

# Set test environment flag before importing any application code
os.environ["TESTING"] = "1"

# Set safe dummy environment variables for local pytest execution
test_env_vars = {
    "OPENAI_API_KEY": "test-openai-key",
    "GROK_API_KEY": "test-grok-key", 
    "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
    "GOOGLE_CLIENT_SECRET": "test-client-secret",
    "DATABASE_URL": "sqlite:///./test.db",
    "CORS_ORIGINS": "http://localhost:3000",
    "DEBUG": "true",
    "LOG_LEVEL": "DEBUG"
}

# Apply test environment variables
for key, value in test_env_vars.items():
    os.environ.setdefault(key, value)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Session-wide test environment setup.
    
    Ensures TESTING=1 is set and all required environment variables
    have safe defaults for testing.
    """
    # Verify test mode is enabled
    assert os.getenv("TESTING") == "1", "Test environment not properly configured"
    
    # Initialize database tables for integration tests
    try:
        from app.database import create_db_and_tables
        create_db_and_tables()
        print("✅ Test database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    # Log test environment setup
    print("✅ Test environment configured with safe defaults")
    print(f"📍 Database: {os.getenv('DATABASE_URL')}")
    print(f"🔑 OpenAI API Key: {os.getenv('OPENAI_API_KEY')[:10]}...")
    print(f"🔑 Grok API Key: {os.getenv('GROK_API_KEY')[:10]}...")
    
    yield
    
    # Cleanup test database
    import sqlite3
    try:
        if os.path.exists("test.db"):
            os.remove("test.db")
            print("🗑️ Test database cleaned up")
    except Exception:
        pass
    
    print("🧹 Test environment cleanup complete")