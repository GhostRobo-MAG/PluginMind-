"""
Comprehensive rate limiting tests.

Tests dual enforcement, IP extraction, token bucket behavior,
and various edge cases for the rate limiting system.
"""

import asyncio
import time
import pytest
from unittest.mock import Mock, patch
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.utils.rate_limit import TokenBucket, RateLimiter
from app.utils.ip import extract_client_ip, _validate_ip
from app.api.dependencies_rate_limit import rate_limiter_dependency, get_rate_limit_key
from app.core.config import settings


class TestTokenBucket:
    """Test token bucket algorithm implementation."""
    
    @pytest.mark.asyncio
    async def test_token_bucket_basic_consumption(self):
        """Test basic token consumption."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        # Should allow initial consumption
        allowed, remaining = await bucket.consume(5)
        assert allowed is True
        assert remaining == 5
        
        # Should allow more consumption within capacity
        allowed, remaining = await bucket.consume(3)
        assert allowed is True
        assert remaining == 2
        
        # Should deny consumption beyond capacity
        allowed, remaining = await bucket.consume(5)
        assert allowed is False
        assert remaining == 2
    
    @pytest.mark.asyncio
    async def test_token_bucket_refill(self):
        """Test token refill over time."""
        bucket = TokenBucket(capacity=10, refill_rate=5.0)  # 5 tokens per second
        
        # Consume all tokens
        await bucket.consume(10)
        
        # Should deny immediately
        allowed, remaining = await bucket.consume(1)
        assert allowed is False
        
        # Wait for refill (0.5 seconds = 2.5 tokens)
        await asyncio.sleep(0.5)
        allowed, remaining = await bucket.consume(2)
        assert allowed is True
        assert remaining >= 0  # Should have some tokens left
    
    @pytest.mark.asyncio
    async def test_token_bucket_capacity_limit(self):
        """Test that tokens don't exceed capacity during refill."""
        bucket = TokenBucket(capacity=5, refill_rate=10.0)
        
        # Wait for potential over-refill
        await asyncio.sleep(1.0)
        
        # Should not exceed capacity
        remaining = await bucket.get_remaining()
        assert remaining <= 5
    
    @pytest.mark.asyncio
    async def test_token_bucket_concurrent_access(self):
        """Test thread safety with concurrent access."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        
        async def consume_tokens():
            for _ in range(10):
                await bucket.consume(1)
        
        # Run multiple concurrent consumers
        tasks = [consume_tokens() for _ in range(5)]
        await asyncio.gather(*tasks)
        
        # Should have consumed 50 tokens total
        remaining = await bucket.get_remaining()
        assert remaining <= 50


class TestRateLimiter:
    """Test rate limiter with multiple buckets."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_separate_keys(self):
        """Test that different keys have separate buckets."""
        limiter = RateLimiter()
        
        # Consume tokens for different keys
        allowed1, _, _ = await limiter.consume("user:123", tokens=5)
        allowed2, _, _ = await limiter.consume("user:456", tokens=5)
        
        assert allowed1 is True
        assert allowed2 is True
    
    @pytest.mark.asyncio
    async def test_rate_limiter_overrides(self):
        """Test capacity and refill rate overrides."""
        limiter = RateLimiter()
        
        # Use custom capacity
        allowed, remaining, _ = await limiter.consume(
            "test:key",
            tokens=50,
            capacity_override=100,
            refill_rate_override=10.0
        )
        
        assert allowed is True
        assert remaining == 50
    
    @pytest.mark.asyncio
    async def test_rate_limiter_retry_after(self):
        """Test retry-after calculation."""
        limiter = RateLimiter()
        
        # Exhaust tokens
        await limiter.consume("test:key", tokens=settings.rate_limit_burst)
        
        # Next request should be denied with retry-after
        allowed, remaining, retry_after = await limiter.consume("test:key", tokens=1)
        
        assert allowed is False
        assert retry_after is not None
        assert retry_after >= 1


class TestIPExtraction:
    """Test IP address extraction utilities."""
    
    def test_validate_ip_valid_ipv4(self):
        """Test valid IPv4 addresses."""
        assert _validate_ip("192.168.1.1") == "192.168.1.1"
        assert _validate_ip("10.0.0.1") == "10.0.0.1"
        assert _validate_ip("127.0.0.1") == "127.0.0.1"
    
    def test_validate_ip_valid_ipv6(self):
        """Test valid IPv6 addresses."""
        assert _validate_ip("::1") == "::1"
        assert _validate_ip("2001:db8::1") == "2001:db8::1"
        assert _validate_ip("fe80::1%lo0") is None  # Zone ID not supported
    
    def test_validate_ip_invalid(self):
        """Test invalid IP addresses."""
        assert _validate_ip("not.an.ip") is None
        assert _validate_ip("999.999.999.999") is None
        assert _validate_ip("") is None
        assert _validate_ip(None) is None
        assert _validate_ip("x" * 50) is None  # Too long
    
    def test_extract_client_ip_direct(self):
        """Test IP extraction from direct client."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {}
        
        ip = extract_client_ip(request)
        assert ip == "192.168.1.1"
    
    def test_extract_client_ip_x_forwarded_for(self):
        """Test IP extraction from X-Forwarded-For header."""
        request = Mock(spec=Request)
        request.client = None
        request.headers = {"x-forwarded-for": "203.0.113.1, 198.51.100.1"}
        
        ip = extract_client_ip(request)
        assert ip == "203.0.113.1"
    
    def test_extract_client_ip_x_real_ip(self):
        """Test IP extraction from X-Real-IP header."""
        request = Mock(spec=Request)
        request.client = None
        request.headers = {"x-real-ip": "203.0.113.2"}
        
        ip = extract_client_ip(request)
        assert ip == "203.0.113.2"
    
    def test_extract_client_ip_fallback(self):
        """Test fallback to 'unknown' when no valid IP found."""
        request = Mock(spec=Request)
        request.client = None
        request.headers = {}
        
        ip = extract_client_ip(request)
        assert ip == "unknown"


class TestRateLimitDependency:
    """Test rate limiting FastAPI dependency."""
    
    @pytest.mark.asyncio
    async def test_unauthenticated_rate_limiting(self):
        """Test rate limiting for unauthenticated users."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {}
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test"
        
        response = Mock(spec=Response)
        response.headers = {}
        
        # Should pass initially
        await rate_limiter_dependency(request, response, credentials=None)
        
        # Should have rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
    
    @pytest.mark.asyncio
    async def test_authenticated_dual_enforcement(self):
        """Test dual enforcement for authenticated users."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {}
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test"
        
        response = Mock(spec=Response)
        response.headers = {}
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "valid.jwt.token"
        
        # Mock JWT verification to return user ID
        with patch('app.api.dependencies_rate_limit.verify_google_id_token') as mock_verify:
            mock_verify.return_value = "user123"
            
            # Should pass with dual enforcement
            await rate_limiter_dependency(request, response, credentials)
            
            # Should have rate limit headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded_response(self):
        """Test 429 response when rate limit exceeded."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {}
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test"
        
        response = Mock(spec=Response)
        response.headers = {}
        
        # Exhaust rate limit first
        with patch('app.api.dependencies_rate_limit.rate_limiter') as mock_limiter:
            # Mock async consume method
            async def mock_consume(*args, **kwargs):
                return (False, 0, 60)  # Denied, 0 remaining, 60s retry
            mock_limiter.consume = mock_consume
            
            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await rate_limiter_dependency(request, response, credentials=None)
            
            assert exc_info.value.status_code == 429
            assert exc_info.value.detail == "Too many requests"
            assert "Retry-After" in response.headers
    
    def test_get_rate_limit_key_authenticated(self):
        """Test rate limit key generation for authenticated users."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {}
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "valid.jwt.token"
        
        with patch('app.api.dependencies_rate_limit.verify_google_id_token') as mock_verify:
            mock_verify.return_value = "user123"
            
            key = get_rate_limit_key(request, credentials)
            assert key == "user:user123"
    
    def test_get_rate_limit_key_unauthenticated(self):
        """Test rate limit key generation for unauthenticated users."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {}
        
        key = get_rate_limit_key(request, credentials=None)
        assert key == "ip:192.168.1.1"
    
    def test_get_rate_limit_key_invalid_token(self):
        """Test rate limit key generation with invalid token."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {}
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "invalid.jwt.token"
        
        with patch('app.api.dependencies_rate_limit.verify_google_id_token') as mock_verify:
            from app.core.exceptions import AuthenticationError
            mock_verify.side_effect = AuthenticationError("Invalid token")
            
            key = get_rate_limit_key(request, credentials)
            assert key == "ip:192.168.1.1"


class TestRateLimitConfiguration:
    """Test rate limit configuration values."""
    
    def test_default_rate_limits(self):
        """Test default rate limit values."""
        assert hasattr(settings, 'rate_limit_per_min')
        assert hasattr(settings, 'rate_limit_burst')
        assert hasattr(settings, 'rate_limit_ip_per_min')
        assert hasattr(settings, 'rate_limit_ip_burst')
        
        # Default values should be reasonable
        assert settings.rate_limit_per_min > 0
        assert settings.rate_limit_burst >= settings.rate_limit_per_min
        assert settings.rate_limit_ip_per_min > settings.rate_limit_per_min
        assert settings.rate_limit_ip_burst >= settings.rate_limit_ip_per_min
    
    def test_ip_limits_higher_than_user_limits(self):
        """Test that IP limits are higher than user limits."""
        assert settings.rate_limit_ip_per_min >= settings.rate_limit_per_min
        assert settings.rate_limit_ip_burst >= settings.rate_limit_burst


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_concurrent_bucket_creation(self):
        """Test concurrent access to bucket creation."""
        limiter = RateLimiter()
        
        async def create_bucket():
            return await limiter._get_or_create_bucket("concurrent:test")
        
        # Create multiple buckets concurrently
        tasks = [create_bucket() for _ in range(10)]
        buckets = await asyncio.gather(*tasks)
        
        # All should reference the same bucket
        first_bucket = buckets[0]
        for bucket in buckets[1:]:
            assert bucket is first_bucket
    
    def test_malformed_headers(self):
        """Test handling of malformed headers."""
        request = Mock(spec=Request)
        request.client = None
        request.headers = {
            "x-forwarded-for": "invalid,ip,addresses",
            "x-real-ip": "not-an-ip"
        }
        
        ip = extract_client_ip(request)
        assert ip == "unknown"
    
    def test_empty_headers(self):
        """Test handling of empty headers."""
        request = Mock(spec=Request)
        request.client = None
        request.headers = {
            "x-forwarded-for": "",
            "x-real-ip": "   "
        }
        
        ip = extract_client_ip(request)
        assert ip == "unknown"
    
    @pytest.mark.asyncio
    async def test_zero_token_consumption(self):
        """Test consuming zero tokens."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        allowed, remaining = await bucket.consume(0)
        assert allowed is True
        assert remaining == 10
    
    @pytest.mark.asyncio
    async def test_negative_token_consumption(self):
        """Test consuming negative tokens (should be treated as 0)."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        allowed, remaining = await bucket.consume(-5)
        assert allowed is True
        assert remaining == 10  # No tokens consumed