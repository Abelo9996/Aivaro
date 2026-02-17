"""
Rate limiting utilities to prevent API abuse and respect provider limits.
"""
import time
import asyncio
from typing import Dict, Optional, Callable
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for a rate limit."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10  # Max concurrent requests


@dataclass
class RateLimitState:
    """Tracks rate limit state for a key."""
    minute_requests: list = field(default_factory=list)
    hour_requests: list = field(default_factory=list)
    concurrent: int = 0
    lock: Lock = field(default_factory=Lock)


class RateLimiter:
    """
    In-memory rate limiter supporting per-user and per-integration limits.
    
    For production, consider using Redis for distributed rate limiting.
    """
    
    # Default limits for different integration providers
    PROVIDER_LIMITS: Dict[str, RateLimitConfig] = {
        "default": RateLimitConfig(requests_per_minute=60, requests_per_hour=1000),
        "google": RateLimitConfig(requests_per_minute=100, requests_per_hour=10000),
        "slack": RateLimitConfig(requests_per_minute=50, requests_per_hour=5000),
        "notion": RateLimitConfig(requests_per_minute=3, requests_per_hour=1000),  # Notion is strict
        "airtable": RateLimitConfig(requests_per_minute=5, requests_per_hour=1000),
        "stripe": RateLimitConfig(requests_per_minute=100, requests_per_hour=10000),
        "openai": RateLimitConfig(requests_per_minute=20, requests_per_hour=500),
        "twilio": RateLimitConfig(requests_per_minute=100, requests_per_hour=5000),
        "hubspot": RateLimitConfig(requests_per_minute=100, requests_per_hour=10000),
        "mailchimp": RateLimitConfig(requests_per_minute=10, requests_per_hour=1000),
    }
    
    # User-level limits
    USER_LIMITS = RateLimitConfig(requests_per_minute=100, requests_per_hour=5000, burst_limit=20)
    
    def __init__(self):
        self._states: Dict[str, RateLimitState] = defaultdict(RateLimitState)
        self._global_lock = Lock()
    
    def _get_state(self, key: str) -> RateLimitState:
        """Get or create rate limit state for a key."""
        if key not in self._states:
            with self._global_lock:
                if key not in self._states:
                    self._states[key] = RateLimitState()
        return self._states[key]
    
    def _clean_old_requests(self, state: RateLimitState, now: float):
        """Remove requests older than the tracking window."""
        minute_ago = now - 60
        hour_ago = now - 3600
        
        state.minute_requests = [t for t in state.minute_requests if t > minute_ago]
        state.hour_requests = [t for t in state.hour_requests if t > hour_ago]
    
    def check_limit(
        self,
        key: str,
        config: Optional[RateLimitConfig] = None
    ) -> tuple[bool, Optional[float]]:
        """
        Check if a request is allowed under rate limits.
        
        Returns:
            (allowed, retry_after) - If not allowed, retry_after is seconds to wait
        """
        config = config or self.PROVIDER_LIMITS["default"]
        state = self._get_state(key)
        now = time.time()
        
        with state.lock:
            self._clean_old_requests(state, now)
            
            # Check minute limit
            if len(state.minute_requests) >= config.requests_per_minute:
                oldest = min(state.minute_requests)
                retry_after = 60 - (now - oldest)
                return False, max(0.1, retry_after)
            
            # Check hour limit
            if len(state.hour_requests) >= config.requests_per_hour:
                oldest = min(state.hour_requests)
                retry_after = 3600 - (now - oldest)
                return False, max(0.1, retry_after)
            
            # Check burst limit
            if state.concurrent >= config.burst_limit:
                return False, 1.0  # Wait a second for concurrent requests
            
            return True, None
    
    def record_request(self, key: str):
        """Record a request for rate limiting."""
        state = self._get_state(key)
        now = time.time()
        
        with state.lock:
            state.minute_requests.append(now)
            state.hour_requests.append(now)
            state.concurrent += 1
    
    def release_request(self, key: str):
        """Release a concurrent request slot."""
        state = self._get_state(key)
        with state.lock:
            state.concurrent = max(0, state.concurrent - 1)
    
    async def acquire(
        self,
        key: str,
        config: Optional[RateLimitConfig] = None,
        timeout: float = 30.0
    ) -> bool:
        """
        Acquire permission to make a request, waiting if necessary.
        
        Returns True if acquired, False if timed out.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            allowed, retry_after = self.check_limit(key, config)
            
            if allowed:
                self.record_request(key)
                return True
            
            if retry_after and retry_after < timeout - (time.time() - start_time):
                logger.debug(f"[RateLimit] Waiting {retry_after:.1f}s for {key}")
                await asyncio.sleep(min(retry_after, 5.0))
            else:
                return False
        
        return False
    
    def get_user_key(self, user_id: str) -> str:
        """Generate rate limit key for a user."""
        return f"user:{user_id}"
    
    def get_provider_key(self, user_id: str, provider: str) -> str:
        """Generate rate limit key for a user+provider combination."""
        return f"user:{user_id}:provider:{provider}"


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


async def check_rate_limit(user_id: str, provider: str = "default") -> None:
    """
    Check rate limits for a user and provider.
    Raises RateLimitExceeded if limits are exceeded.
    """
    config = rate_limiter.PROVIDER_LIMITS.get(provider, rate_limiter.PROVIDER_LIMITS["default"])
    key = rate_limiter.get_provider_key(user_id, provider)
    
    allowed, retry_after = rate_limiter.check_limit(key, config)
    
    if not allowed:
        raise RateLimitExceeded(
            f"Rate limit exceeded for {provider}. Please wait {retry_after:.1f} seconds.",
            retry_after=retry_after
        )
    
    rate_limiter.record_request(key)
