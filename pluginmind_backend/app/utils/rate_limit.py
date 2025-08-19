"""
Token-bucket rate limiter implementation.

Provides in-memory, per-process rate limiting using token bucket algorithm
with asyncio locks for thread safety.
"""

import asyncio
import time
from typing import Dict, Optional, Tuple

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TokenBucket:
    """
    Token bucket rate limiter implementation.
    
    Allows burst traffic up to bucket capacity while maintaining
    steady refill rate for sustained usage.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens (burst size)
            refill_rate: Tokens per second refill rate
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> Tuple[bool, int]:
        """
        Attempt to consume tokens from bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            Tuple of (success: bool, remaining_tokens: int)
        """
        async with self.lock:
            now = time.time()
            
            # Refill bucket based on time elapsed
            time_elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + (time_elapsed * self.refill_rate)
            )
            self.last_refill = now
            
            # Treat negative tokens as zero consumption
            if tokens < 0:
                tokens = 0
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True, int(self.tokens)
            else:
                return False, int(self.tokens)
    
    async def get_remaining(self) -> int:
        """Get current number of tokens without consuming."""
        async with self.lock:
            now = time.time()
            time_elapsed = now - self.last_refill
            current_tokens = min(
                self.capacity,
                self.tokens + (time_elapsed * self.refill_rate)
            )
            return int(current_tokens)


class RateLimiter:
    """
    Global rate limiter managing multiple token buckets by key.
    
    Uses in-memory storage suitable for single-process deployments.
    """
    
    def __init__(self):
        """Initialize rate limiter with configured settings."""
        self.buckets: Dict[str, TokenBucket] = {}
        self.capacity = settings.rate_limit_burst
        self.refill_rate = settings.rate_limit_per_min / 60.0  # Convert per-minute to per-second
        self.lock = asyncio.Lock()
        
        logger.info(
            f"Rate limiter initialized: capacity={self.capacity}, "
            f"refill_rate={self.refill_rate:.2f}/sec ({settings.rate_limit_per_min}/min)"
        )
    
    async def _get_or_create_bucket(self, key: str, capacity_override: Optional[int] = None, refill_rate_override: Optional[float] = None) -> TokenBucket:
        """Get existing bucket or create new one for key."""
        async with self.lock:
            if key not in self.buckets:
                effective_capacity = capacity_override or self.capacity
                effective_refill_rate = refill_rate_override or self.refill_rate
                self.buckets[key] = TokenBucket(effective_capacity, effective_refill_rate)
                logger.debug(f"Created new rate limit bucket for key: {key} (capacity={effective_capacity}, refill_rate={effective_refill_rate:.2f})")
            return self.buckets[key]
    
    async def consume(self, key: str, tokens: int = 1, capacity_override: Optional[int] = None, refill_rate_override: Optional[float] = None) -> Tuple[bool, int, Optional[int]]:
        """
        Attempt to consume tokens for given key.
        
        Args:
            key: Rate limit key (e.g., "user:123" or "ip:1.2.3.4")
            tokens: Number of tokens to consume
            capacity_override: Override bucket capacity for this call
            refill_rate_override: Override refill rate for this call
            
        Returns:
            Tuple of (allowed: bool, remaining_tokens: int, retry_after_seconds: Optional[int])
        """
        bucket = await self._get_or_create_bucket(key, capacity_override, refill_rate_override)
        allowed, remaining = await bucket.consume(tokens)
        
        # Use override refill rate for retry calculation if provided
        effective_refill_rate = refill_rate_override or self.refill_rate
        
        retry_after = None
        if not allowed:
            # Calculate retry-after based on how long it takes to refill needed tokens
            needed_tokens = tokens - remaining
            retry_after = max(1, int(needed_tokens / effective_refill_rate))
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for key: {key} (remaining: {remaining})")
        else:
            logger.debug(f"Rate limit check passed for key: {key} (remaining: {remaining})")
        
        return allowed, remaining, retry_after
    
    async def get_remaining(self, key: str) -> int:
        """Get remaining tokens for key without consuming."""
        bucket = await self._get_or_create_bucket(key)
        return await bucket.get_remaining()


# Global rate limiter instance
rate_limiter = RateLimiter()