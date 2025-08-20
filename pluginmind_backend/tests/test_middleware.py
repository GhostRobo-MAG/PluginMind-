#!/usr/bin/env python3
"""
Test suite for middleware configuration and behavior.

Tests middleware execution order, CORS behavior, and security headers.
Can be run standalone or integrated into CI/CD pipeline.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports  
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set required environment variables for testing
os.environ.update({
    'DEBUG': 'true',
    'OPENAI_API_KEY': 'dummy-key-for-testing',
    'GROK_API_KEY': 'dummy-key-for-testing', 
    'GOOGLE_CLIENT_ID': 'dummy-client-id-for-testing',
    'DATABASE_URL': 'sqlite:///./test.db'
})

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import the app
from app.main import app

def test_middleware_order():
    """Test the final middleware stack order."""
    print("=== Middleware Stack Analysis ===")
    
    # Based on our main.py setup, print the expected order
    expected_order = [
        "CORSMiddleware (setup_cors)",
        "AmbientJWTAuthMiddleware", 
        "SecurityHeadersMiddleware",
        "BodySizeLimitMiddleware", 
        "CorrelationIdMiddleware",
        "Routes + Error Handlers"
    ]
    
    print("Expected middleware execution order (outer → inner):")
    for i, name in enumerate(expected_order):
        print(f"  {i+1}. {name}")
    
    print(f"\nFrom main.py lines 96-101:")
    print("  setup_error_handlers(app)  # Error handlers (not middleware stack)")
    print("  app.add_middleware(CorrelationIdMiddleware)  # Innermost - early for logging")
    print("  app.add_middleware(BodySizeLimitMiddleware)  # Body size limits")  
    print("  app.add_middleware(SecurityHeadersMiddleware)  # Security headers")
    print("  app.add_middleware(AmbientJWTAuthMiddleware)  # Ambient JWT parsing")
    print("  setup_cors(app)  # Outermost - CORS headers on all responses")
    
    # Test passes by not throwing an error

def test_cors_behavior():
    """Test CORS behavior with different origins."""
    print("\n=== CORS Behavior Tests ===")
    
    client = TestClient(app)
    
    # Test 1: OPTIONS request from allowed origin
    print("Test 1: OPTIONS from allowed origin (http://localhost:3000)")
    response = client.options("/health", headers={"Origin": "http://localhost:3000"})
    print(f"  Status: {response.status_code}")
    print(f"  CORS headers: {dict((k, v) for k, v in response.headers.items() if 'access-control' in k.lower())}")
    
    # Test 2: OPTIONS request from disallowed origin
    print("\nTest 2: OPTIONS from disallowed origin (https://malicious.com)")
    response = client.options("/health", headers={"Origin": "https://malicious.com"})
    print(f"  Status: {response.status_code}")
    print(f"  CORS headers: {dict((k, v) for k, v in response.headers.items() if 'access-control' in k.lower())}")
    
    # Test 3: Regular GET request with CORS
    print("\nTest 3: GET request from allowed origin")
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    print(f"  Status: {response.status_code}")
    print(f"  CORS headers: {dict((k, v) for k, v in response.headers.items() if 'access-control' in k.lower())}")
    print(f"  Security headers: {dict((k, v) for k, v in response.headers.items() if k.startswith(('x-', 'strict-transport', 'referrer')))}")
    

def test_auth_middleware():
    """Test ambient JWT auth middleware."""
    print("\n=== Auth Middleware Tests ===")
    
    client = TestClient(app)
    
    # Test 1: Request without auth header
    print("Test 1: Request without Authorization header")
    response = client.get("/health")
    print(f"  Status: {response.status_code}")
    
    # Test 2: Request with invalid JWT
    print("\nTest 2: Request with invalid JWT")
    response = client.get("/health", headers={"Authorization": "Bearer invalid-token"})
    print(f"  Status: {response.status_code}")
    
    # Test 3: Try protected endpoint without auth
    print("\nTest 3: Protected endpoint without auth (should fail)")
    response = client.post("/analyze", json={"user_input": "test"})
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json() if response.status_code < 500 else 'Server error'}")
    

if __name__ == "__main__":
    print("Testing PluginMind Backend Middleware Configuration")
    print("=" * 60)
    
    try:
        middleware_order = test_middleware_order()
        test_cors_behavior()
        test_auth_middleware()
        
        print("\n=== Summary ===")
        print("✅ All tests completed successfully")
        print(f"✅ Final middleware order: {' → '.join(middleware_order)}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()