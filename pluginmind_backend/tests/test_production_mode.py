#!/usr/bin/env python3
"""
Test production mode CORS configuration.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

def test_production_cors_config():
    """Test that CORS_ORIGINS is required in production mode."""
    print("=== Production CORS Configuration Test ===")
    
    # Test 1: Production mode without CORS_ORIGINS should fail
    print("Test 1: Production mode without CORS_ORIGINS (should fail)")
    os.environ.update({
        'DEBUG': 'false',  # Production mode
        'OPENAI_API_KEY': 'dummy-key',
        'GROK_API_KEY': 'dummy-key', 
        'GOOGLE_CLIENT_ID': 'dummy-client-id',
        'DATABASE_URL': 'sqlite:///./test.db'
    })
    
    # Remove CORS_ORIGINS if set
    os.environ.pop('CORS_ORIGINS', None)
    
    try:
        from app.core.config import Settings
        settings = Settings()
        print("  ❌ FAILED: Should have raised ValueError")
    except ValueError as e:
        if "CORS_ORIGINS environment variable is required in production" in str(e):
            print("  ✅ PASSED: Correctly requires CORS_ORIGINS in production")
        else:
            print(f"  ❌ FAILED: Wrong error message: {e}")
    except Exception as e:
        print(f"  ❌ FAILED: Unexpected error: {e}")
    
    # Test 2: Production mode with CORS_ORIGINS should work
    print("\nTest 2: Production mode with CORS_ORIGINS (should work)")
    os.environ['CORS_ORIGINS'] = 'https://example.com,https://app.example.com'
    
    try:
        # Clear module cache to reload config
        if 'app.core.config' in sys.modules:
            del sys.modules['app.core.config']
        
        from app.core.config import Settings
        settings = Settings()
        print(f"  ✅ PASSED: CORS origins: {settings.cors_origins}")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
    
    # Test 3: Debug mode should work with default
    print("\nTest 3: Debug mode should use default localhost:3000")
    os.environ.update({
        'DEBUG': 'true'  # Debug mode
    })
    os.environ.pop('CORS_ORIGINS', None)
    
    try:
        # Clear module cache to reload config
        if 'app.core.config' in sys.modules:
            del sys.modules['app.core.config']
        
        from app.core.config import Settings
        settings = Settings()
        print(f"  ✅ PASSED: Debug CORS origins: {settings.cors_origins}")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")

if __name__ == "__main__":
    test_production_cors_config()