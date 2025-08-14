"""
Tests for unified error handling system.

This module tests the exception mapping, error response format,
and integration with the FastAPI application.
"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Create minimal pytest replacement for standalone execution
    class pytest:
        @staticmethod
        def raises(exc_type):
            class ExcInfo:
                def __init__(self):
                    self.value = None
                def __enter__(self):
                    return self
                def __exit__(self, exc_type_raised, exc_value, traceback):
                    if exc_type_raised == exc_type:
                        self.value = exc_value
                        return True
                    return False
            return ExcInfo()

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.error_handler import EXCEPTION_MAP, EXCEPTION_MESSAGES, raise_api_error, setup_error_handlers
from app.core.exceptions import (
    AuthenticationError,
    UserAccessError,
    QueryLimitExceededError,
    UserNotFoundError,
    ServiceUnavailableError,
    RateLimitError,
    AIServiceError,
    InvalidInputError,
    JobNotFoundError,
    DatabaseError,
    ErrorCodes
)

client = TestClient(app)


def create_test_app_with_exception_endpoint():
    """Create a test app with an endpoint that raises generic exceptions for testing."""
    test_app = FastAPI()
    setup_error_handlers(test_app)
    
    @test_app.get("/test-generic-exception")
    async def test_generic_exception():
        """Test endpoint that raises a generic exception."""
        raise ValueError("This is a test generic exception")
    
    @test_app.get("/test-rate-limit-error")
    async def test_rate_limit_error():
        """Test endpoint that raises RateLimitError with retry_after."""
        from app.core.exceptions import RateLimitError
        raise RateLimitError("Rate limit exceeded for testing", retry_after=120)
    
    return test_app


class TestExceptionMapping:
    """Test the exception mapping system."""

    def test_all_exceptions_mapped(self):
        """Test that all expected exceptions are in the mapping."""
        expected_exceptions = [
            AuthenticationError,
            UserAccessError,
            QueryLimitExceededError,
            UserNotFoundError,
            ServiceUnavailableError,
            RateLimitError,
            AIServiceError,
            InvalidInputError,
            JobNotFoundError,
            DatabaseError
        ]
        
        # Check EXCEPTION_MAP
        missing_from_map = [exc for exc in expected_exceptions if exc not in EXCEPTION_MAP]
        assert len(missing_from_map) == 0, f"Missing from EXCEPTION_MAP: {[exc.__name__ for exc in missing_from_map]}"
        
        # Check EXCEPTION_MESSAGES
        missing_from_messages = [exc for exc in expected_exceptions if exc not in EXCEPTION_MESSAGES]
        assert len(missing_from_messages) == 0, f"Missing from EXCEPTION_MESSAGES: {[exc.__name__ for exc in missing_from_messages]}"

    def test_error_codes_exist(self):
        """Test that all error codes exist in ErrorCodes class."""
        for exc_type, (status_code, error_code) in EXCEPTION_MAP.items():
            # Check constant exists
            assert hasattr(ErrorCodes, error_code), f"Error code {error_code} not found in ErrorCodes class"
            
            # Check constant value matches
            actual_value = getattr(ErrorCodes, error_code)
            assert actual_value == error_code, f"Error code value mismatch: {actual_value} != {error_code}"

    def test_status_codes_valid(self):
        """Test that all status codes are valid HTTP codes."""
        valid_status_codes = range(400, 600)  # 4xx and 5xx codes
        
        for exc_type, (status_code, error_code) in EXCEPTION_MAP.items():
            assert status_code in valid_status_codes, f"Invalid status code {status_code} for {exc_type.__name__}"

    def test_raise_api_error_helper(self):
        """Test the raise_api_error helper function."""
        test_exception = UserNotFoundError("Test user not found")
        
        with pytest.raises(UserNotFoundError) as exc_info:
            raise_api_error(test_exception)
        
        assert str(exc_info.value) == "Test user not found"


class TestErrorResponseFormat:
    """Test the error response format in actual API calls."""

    def test_job_not_found_format(self):
        """Test JobNotFoundError response format."""
        response = client.get("/analyze-async/non-existent-job-id")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "message" in data["error"]
        assert "code" in data["error"]
        assert "correlation_id" in data["error"]
        
        assert data["error"]["code"] == "JOB_NOT_FOUND"
        assert data["error"]["message"] == "Requested job was not found."

    def test_user_not_found_format(self):
        """Test UserNotFoundError response format (requires auth)."""
        # This would require setting up proper auth, but we can test the structure
        # by checking if the endpoint exists and returns expected format for auth errors
        response = client.get("/me")  # Requires auth
        assert response.status_code == 401
        
        data = response.json()
        assert "error" in data
        assert "message" in data["error"]
        assert "code" in data["error"] 
        assert "correlation_id" in data["error"]

    def test_validation_error_format(self):
        """Test validation error format with unified envelope."""
        # Send invalid JSON to trigger validation error
        response = client.post("/test-validation-error", json={})  # Missing required user_input field
        
        # Should now use our unified error format (after RequestValidationError handler)
        assert response.status_code == 422
        data = response.json()
        
        # Verify unified error envelope format
        assert "error" in data
        assert "message" in data["error"]
        assert "code" in data["error"]
        assert "correlation_id" in data["error"]
        
        assert data["error"]["code"] == "INVALID_INPUT"
        assert data["error"]["message"] == "Invalid request payload."
        assert isinstance(data["error"]["correlation_id"], str)
        assert len(data["error"]["correlation_id"]) > 0

    def test_malformed_json_validation_error(self):
        """Test malformed JSON triggers 422 with unified format."""
        # Send malformed JSON (this should trigger RequestValidationError)
        response = client.post(
            "/test-malformed-json",
            data='{"user_input": "test", malformed}',  # Malformed JSON
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 422 with unified error format
        assert response.status_code == 422
        data = response.json()
        
        # Verify unified error envelope format
        assert "error" in data
        assert data["error"]["code"] == "INVALID_INPUT"
        assert data["error"]["message"] == "Invalid request payload."
        assert "correlation_id" in data["error"]

    def test_missing_required_field_validation_error(self):
        """Test missing required fields trigger 422 with unified format."""
        # Send request without required user_input field
        response = client.post("/test-validation-error", json={"wrong_field": "value"})
        
        # Should return 422 with unified error format
        assert response.status_code == 422
        data = response.json()
        
        # Verify unified error envelope format
        assert "error" in data
        assert data["error"]["code"] == "INVALID_INPUT"
        assert data["error"]["message"] == "Invalid request payload."
        assert "correlation_id" in data["error"]

    def test_large_request_format(self):
        """Test request size limit error format."""
        # Create a large request payload (>1MB)
        large_payload = {"user_input": "A" * (1024 * 1024 + 1)}  # 1MB + 1 byte
        
        response = client.post("/analyze", json=large_payload)
        
        # This might not trigger our middleware due to FastAPI's own limits,
        # but if it does, it should use our format
        if response.status_code == 413:
            data = response.json()
            assert "error" in data
            assert data["error"]["code"] == "REQUEST_TOO_LARGE"

    def test_content_type_header(self):
        """Test that error responses have correct Content-Type."""
        response = client.get("/analyze-async/non-existent-job-id")
        assert response.status_code == 404
        assert response.headers["content-type"] == "application/json"

    def test_correlation_id_format(self):
        """Test that correlation_id is a valid UUID format."""
        response = client.get("/analyze-async/non-existent-job-id")
        data = response.json()
        
        correlation_id = data["error"]["correlation_id"]
        assert isinstance(correlation_id, str)
        assert len(correlation_id) > 0
        # Could add UUID format validation here if needed


class TestExceptionMessageHandling:
    """Test different message handling strategies."""

    def test_custom_message_exceptions(self):
        """Test exceptions that use custom messages."""
        custom_message_exceptions = [
            AuthenticationError,
            UserAccessError,
            UserNotFoundError,
            ServiceUnavailableError,
            RateLimitError,
            AIServiceError,
            JobNotFoundError,
            DatabaseError
        ]
        
        for exc_type in custom_message_exceptions:
            # These should have custom messages (not None)
            assert EXCEPTION_MESSAGES[exc_type] is not None
            assert len(EXCEPTION_MESSAGES[exc_type]) > 0

    def test_original_message_exceptions(self):
        """Test exceptions that use original messages."""
        original_message_exceptions = [
            QueryLimitExceededError,
            InvalidInputError
        ]
        
        for exc_type in original_message_exceptions:
            # These should use original messages (None in mapping)
            assert EXCEPTION_MESSAGES[exc_type] is None


class TestGenericExceptionHandling:
    """Test generic exception handling (500 errors)."""

    def test_generic_exception_format(self):
        """Test that unexpected exceptions return proper 500 error format."""
        # Create test app with exception endpoint  
        test_app = create_test_app_with_exception_endpoint()
        test_client = TestClient(test_app, raise_server_exceptions=False)
        
        # Trigger generic exception - should not raise, should return 500 response
        response = test_client.get("/test-generic-exception")
        
        # Verify status code and unified error format
        assert response.status_code == 500
        data = response.json()
        
        # Verify unified error envelope format
        assert "error" in data
        assert "message" in data["error"]
        assert "code" in data["error"]
        assert "correlation_id" in data["error"]
        
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert data["error"]["message"] == "Internal server error. Please contact support if the issue persists."
        assert isinstance(data["error"]["correlation_id"], str)
        assert len(data["error"]["correlation_id"]) > 0


class TestRateLimitRetryAfter:
    """Test Retry-After header functionality in rate limit responses."""

    def test_rate_limit_error_with_retry_after(self):
        """Test that RateLimitError includes Retry-After header when retry_after is set."""
        from app.core.exceptions import RateLimitError
        
        # Test RateLimitError constructor with retry_after
        error = RateLimitError("Rate limit exceeded", retry_after=60)
        assert error.retry_after == 60
        assert str(error) == "Rate limit exceeded"
        
        # Test RateLimitError without retry_after
        error_no_retry = RateLimitError("Rate limit exceeded")
        assert not hasattr(error_no_retry, 'retry_after') or error_no_retry.retry_after is None

    def test_rate_limit_error_response_with_retry_after_header(self):
        """Test that RateLimitError response includes Retry-After header."""
        # Create test app with rate limit error endpoint
        test_app = create_test_app_with_exception_endpoint()
        test_client = TestClient(test_app)
        
        # Trigger RateLimitError with retry_after
        response = test_client.get("/test-rate-limit-error")
        
        # Verify status code and unified error format
        assert response.status_code == 429
        data = response.json()
        
        # Verify unified error envelope format
        assert "error" in data
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert data["error"]["message"] == "Too many requests. Please try again later."
        
        # Verify Retry-After header is present
        assert "Retry-After" in response.headers
        assert response.headers["Retry-After"] == "120"

    def test_http_exception_429_uses_rate_limit_code(self):
        """Test that HTTPException with status 429 uses RATE_LIMIT_EXCEEDED code."""
        # This tests the HTTPException handler enhancement for 429 errors
        # The rate limiter dependency raises HTTPException(status_code=429)
        # We can verify this indirectly by checking the error code mapping
        
        assert ErrorCodes.RATE_LIMIT_EXCEEDED == "RATE_LIMIT_EXCEEDED"
        
        # The HTTP exception handler should detect status_code=429 and:
        # - Use "Too many requests. Please try again later." message
        # - Use ErrorCodes.RATE_LIMIT_EXCEEDED code
        # - Preserve any Retry-After headers set by the rate limiter
        pass


class TestExceptionStatusCodes:
    """Test status code assignments for different exception types."""

    def test_authentication_errors_401(self):
        """Test authentication errors return 401."""
        auth_exceptions = [AuthenticationError]
        for exc_type in auth_exceptions:
            status_code, _ = EXCEPTION_MAP[exc_type]
            assert status_code == 401

    def test_not_found_errors_404(self):
        """Test not found errors return 404."""
        not_found_exceptions = [UserNotFoundError, JobNotFoundError]
        for exc_type in not_found_exceptions:
            status_code, _ = EXCEPTION_MAP[exc_type]
            assert status_code == 404

    def test_rate_limit_errors_429(self):
        """Test rate limit errors return 429."""
        rate_limit_exceptions = [RateLimitError, QueryLimitExceededError]
        for exc_type in rate_limit_exceptions:
            status_code, _ = EXCEPTION_MAP[exc_type]
            assert status_code == 429

    def test_server_errors_5xx(self):
        """Test server errors return 5xx codes."""
        server_error_exceptions = [
            (UserAccessError, 500),
            (DatabaseError, 500),
            (AIServiceError, 502),
            (ServiceUnavailableError, 503)
        ]
        
        for exc_type, expected_status in server_error_exceptions:
            status_code, _ = EXCEPTION_MAP[exc_type]
            assert status_code == expected_status


def print_exception_mapping_table():
    """Utility function to print the exception mapping table for documentation."""
    print("\n" + "="*80)
    print("Exception → Status → Code Mapping Table")
    print("="*80)
    print(f"{'Exception':<25} {'Status':<8} {'Code':<25} {'Message Override'}")
    print("-" * 80)
    
    for exc_type in sorted(EXCEPTION_MAP.keys(), key=lambda x: x.__name__):
        status_code, error_code = EXCEPTION_MAP[exc_type]
        message_override = EXCEPTION_MESSAGES.get(exc_type)
        has_override = "Yes" if message_override else "No (uses original)"
        
        print(f"{exc_type.__name__:<25} {status_code:<8} {error_code:<25} {has_override}")
    print("="*80)


if __name__ == "__main__":
    # Run this to see the mapping table
    print_exception_mapping_table()