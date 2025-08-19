#!/usr/bin/env python3
"""
JWT Security Test Suite

Tests security hardening measures applied to JWT authentication:
- Error message sanitization
- PII removal from logs  
- Dynamic issuer discovery
- Configuration validation
- Attack vector prevention

Can be run standalone or integrated into CI/CD pipeline.
"""

import os
import sys
import json
import logging
from unittest.mock import patch, MagicMock
from pathlib import Path
from io import StringIO

# Add parent directory to path for imports  
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set required environment variables for testing
os.environ.update({
    'DEBUG': 'true',
    'OPENAI_API_KEY': 'dummy-key-for-testing',
    'GROK_API_KEY': 'dummy-key-for-testing', 
    'GOOGLE_CLIENT_ID': 'test-client-id.googleusercontent.com',
    'GOOGLE_CLIENT_SECRET': 'test-client-secret',
    'DATABASE_URL': 'sqlite:///./test.db'
})

from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.auth import verify_google_id_token_claims, verify_google_id_token
from app.core.config import Settings

def test_error_message_sanitization():
    """Test that JWT error messages don't leak implementation details."""
    print("=== Error Message Sanitization Tests ===")
    
    # Mock malformed tokens that would cause different Google library errors
    test_cases = [
        {
            'token': 'not.a.jwt.token',
            'expected_detail': 'Invalid token format',
            'description': 'Malformed JWT format'
        },
        {
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.invalid_signature',
            'expected_detail': 'Invalid token format',
            'description': 'Invalid signature'
        }
    ]
    
    results = []
    for case in test_cases:
        print(f"\nTest: {case['description']}")
        try:
            verify_google_id_token_claims(case['token'])
            print(f"  ❌ FAIL: Should have raised HTTPException")
            results.append(False)
        except HTTPException as e:
            if e.detail == case['expected_detail']:
                print(f"  ✅ PASS: Correct sanitized error: '{e.detail}'")
                results.append(True)
            else:
                print(f"  ❌ FAIL: Wrong error message: '{e.detail}'")
                print(f"    Expected: '{case['expected_detail']}'")
                results.append(False)
        except Exception as e:
            print(f"  ❌ FAIL: Unexpected exception: {type(e).__name__}: {e}")
            results.append(False)
    
    return all(results)

def test_pii_removal_from_logs():
    """Test that debug logs don't contain user identifiers."""
    print("\n=== PII Removal from Logs Tests ===")
    
    # Capture log output
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    
    # Get the auth logger and add our handler
    from app.middleware.auth import logger
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    client = TestClient(app)
    
    try:
        # Test case 1: Successful auth debug log
        print("Test 1: Authentication success log (should not contain user ID)")
        
        # Mock a scenario where auth would succeed (though token is invalid)
        # We're testing the log message format, not actual auth
        with patch('app.middleware.auth.verify_google_id_token') as mock_verify:
            mock_verify.return_value = "test-user@example.com"
            
            # This will trigger the debug log in get_current_user
            try:
                from app.middleware.auth import get_current_user
                from fastapi.security import HTTPAuthorizationCredentials
                
                credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake-token")
                get_current_user(credentials)
            except Exception:
                pass  # We expect this to fail, we're just testing the log
        
        # Test case 2: Ambient middleware log 
        print("Test 2: Ambient middleware log (should not contain user ID)")
        
        response = client.get("/health", headers={"Authorization": "Bearer fake-token"})
        
        # Check captured logs
        log_output = log_capture.getvalue()
        print(f"Captured log output length: {len(log_output)} characters")
        
        # Check for PII leakage
        sensitive_patterns = [
            '@example.com',
            'test-user',
            'user_id',
            'Authentication successful for user:',
            'Set ambient user in request state:'
        ]
        
        pii_found = []
        for pattern in sensitive_patterns:
            if pattern in log_output:
                pii_found.append(pattern)
        
        if pii_found:
            print(f"  ❌ FAIL: Found PII in logs: {pii_found}")
            print(f"  Log output: {log_output[:500]}...")
            return False
        else:
            print("  ✅ PASS: No PII found in debug logs")
            return True
            
    finally:
        # Clean up
        logger.removeHandler(handler)

def test_dynamic_issuer_discovery():
    """Test dynamic issuer discovery with fallback."""
    print("\n=== Dynamic Issuer Discovery Tests ===")
    
    # Test 1: Successful discovery
    print("Test 1: Successful OpenID discovery")
    
    mock_discovery_response = {
        'issuer': 'https://accounts.google.com',
        'authorization_endpoint': 'https://accounts.google.com/o/oauth2/auth',
        'token_endpoint': 'https://oauth2.googleapis.com/token'
    }
    
    with patch('app.middleware.auth.http_requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_discovery_response
        mock_get.return_value = mock_response
        
        # Mock Google's token verification to return valid claims
        with patch('app.middleware.auth.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.return_value = {
                'iss': 'https://accounts.google.com',  # Matches discovered issuer
                'aud': 'test-client-id.googleusercontent.com',
                'sub': '1234567890',
                'email': 'test@example.com'
            }
            
            try:
                result = verify_google_id_token_claims('fake-valid-token')
                print("  ✅ PASS: Dynamic issuer discovery successful")
                return True
            except HTTPException as e:
                print(f"  ❌ FAIL: Unexpected error: {e.detail}")
                return False
    
    # Test 2: Discovery failure with fallback
    print("\nTest 2: Discovery failure with fallback")
    
    with patch('app.middleware.auth.http_requests.get') as mock_get:
        # Simulate network error
        mock_get.side_effect = Exception("Network error")
        
        # Mock Google's token verification
        with patch('app.middleware.auth.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.return_value = {
                'iss': 'https://accounts.google.com',  # Should match fallback
                'aud': 'test-client-id.googleusercontent.com', 
                'sub': '1234567890',
                'email': 'test@example.com'
            }
            
            try:
                result = verify_google_id_token_claims('fake-valid-token')
                print("  ✅ PASS: Fallback issuer validation successful")
                return True
            except HTTPException as e:
                print(f"  ❌ FAIL: Fallback failed: {e.detail}")
                return False

def test_config_validation():
    """Test enhanced configuration validation."""
    print("\n=== Configuration Validation Tests ===")
    
    # Test 1: Invalid GOOGLE_CLIENT_ID format
    print("Test 1: Invalid GOOGLE_CLIENT_ID format")
    
    # Temporarily set invalid Google Client ID and disable test mode
    original_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    original_testing = os.environ.pop('TESTING', None)
    
    # Set an invalid Google Client ID (doesn't end with .apps.googleusercontent.com)
    os.environ['GOOGLE_CLIENT_ID'] = 'invalid-client-id'
    
    try:
        settings = Settings()
        print("  ❌ FAIL: Should have raised ValueError for invalid GOOGLE_CLIENT_ID")
        return False
    except ValueError as e:
        if "GOOGLE_CLIENT_ID is missing or invalid format" in str(e):
            print("  ✅ PASS: Correctly validates GOOGLE_CLIENT_ID format requirement")
            result = True
        else:
            print(f"  ❌ FAIL: Wrong error message: {e}")
            result = False
    finally:
        # Restore the original env vars
        if original_client_id:
            os.environ['GOOGLE_CLIENT_ID'] = original_client_id
        if original_testing:
            os.environ['TESTING'] = original_testing
    
    # Test 2: All required vars present
    print("\nTest 2: All required variables present")
    os.environ['GOOGLE_CLIENT_SECRET'] = 'test-secret'
    
    try:
        settings = Settings()
        print("  ✅ PASS: Configuration loads successfully with all variables")
        return result and True
    except Exception as e:
        print(f"  ❌ FAIL: Unexpected error: {e}")
        return False

def test_attack_vector_prevention():
    """Test prevention of common JWT attack vectors."""
    print("\n=== Attack Vector Prevention Tests ===")
    
    client = TestClient(app)
    
    # Test 1: Algorithm confusion attack (using 'none' algorithm)
    print("Test 1: Algorithm confusion attack")
    
    # Create a token with 'none' algorithm
    fake_none_token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhdHRhY2tlciIsImF1ZCI6InRlc3QtY2xpZW50LWlkLmdvb2dsZXVzZXJjb250ZW50LmNvbSJ9."
    
    response = client.post(
        "/analyze", 
        json={"user_input": "test"},
        headers={"Authorization": f"Bearer {fake_none_token}"}
    )
    
    if response.status_code == 401:
        print("  ✅ PASS: 'none' algorithm attack blocked")
        attack_test_1 = True
    else:
        print(f"  ❌ FAIL: Should have returned 401, got {response.status_code}")
        attack_test_1 = False
    
    # Test 2: Token in wrong location (query param)
    print("\nTest 2: Token in query parameter (should be ignored)")
    
    response = client.post("/analyze?access_token=malicious-token", json={"user_input": "test"})
    
    # Check for 401 status and our unified error format
    response_data = response.json()
    if (response.status_code == 401 and 
        response_data.get('error', {}).get('code') == 'AUTHENTICATION_FAILED'):
        print("  ✅ PASS: Query parameter tokens ignored")
        attack_test_2 = True
    else:
        print(f"  ❌ FAIL: Should require Authorization header")
        print(f"    Got status: {response.status_code}, response: {response_data}")
        attack_test_2 = False
    
    # Test 3: Multiple Authorization headers
    print("\nTest 3: Multiple Authorization headers")
    
    response = client.post(
        "/analyze",
        json={"user_input": "test"},
        headers={
            "Authorization": "Bearer token1",
            "authorization": "Bearer token2"  # Different case
        }
    )
    
    # Should still return 401 (invalid token), not crash
    if response.status_code == 401:
        print("  ✅ PASS: Multiple auth headers handled gracefully")
        attack_test_3 = True
    else:
        print(f"  ❌ FAIL: Unexpected status code: {response.status_code}")
        attack_test_3 = False
    
    return all([attack_test_1, attack_test_2, attack_test_3])

def main():
    """Run all JWT security tests."""
    print("JWT Authentication Security Test Suite")
    print("=" * 60)
    
    test_results = []
    
    try:
        # Run all test suites
        test_results.append(("Error Message Sanitization", test_error_message_sanitization()))
        test_results.append(("PII Removal from Logs", test_pii_removal_from_logs()))
        test_results.append(("Dynamic Issuer Discovery", test_dynamic_issuer_discovery())) 
        test_results.append(("Configuration Validation", test_config_validation()))
        test_results.append(("Attack Vector Prevention", test_attack_vector_prevention()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} test suites passed")
        
        if passed == total:
            print("🎉 All JWT security tests passed!")
            return True
        else:
            print("🚨 Some security tests failed - review implementation")
            return False
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)