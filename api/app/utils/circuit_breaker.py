"""
Circuit breaker pattern implementation for fault tolerance.
Prevents cascading failures when external services are down.
"""
import time
import asyncio
from enum import Enum
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for a circuit breaker."""
    failure_threshold: int = 5        # Failures before opening circuit
    success_threshold: int = 3        # Successes in half-open to close
    timeout: float = 30.0             # Seconds before trying half-open
    half_open_max_calls: int = 3      # Max concurrent calls in half-open


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.
    
    States:
    - CLOSED: Normal operation, tracking failures
    - OPEN: Service is down, immediately reject requests
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
        self._lock = Lock()
    
    def _should_attempt(self) -> tuple[bool, Optional[str]]:
        """Check if a request should be attempted."""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True, None
            
            if self.state == CircuitState.OPEN:
                # Check if timeout has passed
                if self.last_failure_time:
                    elapsed = time.time() - self.last_failure_time
                    if elapsed >= self.config.timeout:
                        self.state = CircuitState.HALF_OPEN
                        self.half_open_calls = 0
                        self.success_count = 0
                        logger.info(f"[CircuitBreaker] {self.name}: OPEN -> HALF_OPEN")
                        return True, None
                
                return False, f"Circuit breaker {self.name} is OPEN"
            
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls < self.config.half_open_max_calls:
                    self.half_open_calls += 1
                    return True, None
                return False, f"Circuit breaker {self.name} is testing recovery"
        
        return True, None
    
    def record_success(self):
        """Record a successful call."""
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    logger.info(f"[CircuitBreaker] {self.name}: HALF_OPEN -> CLOSED (recovered)")
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self, error: Optional[Exception] = None):
        """Record a failed call."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open goes back to open
                self.state = CircuitState.OPEN
                logger.warning(f"[CircuitBreaker] {self.name}: HALF_OPEN -> OPEN (failure: {error})")
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning(
                        f"[CircuitBreaker] {self.name}: CLOSED -> OPEN "
                        f"(failures: {self.failure_count}, error: {error})"
                    )
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state as dict."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time,
        }


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = Lock()
        
        # Default configs for known services
        self._configs: Dict[str, CircuitBreakerConfig] = {
            "google": CircuitBreakerConfig(failure_threshold=5, timeout=60),
            "slack": CircuitBreakerConfig(failure_threshold=5, timeout=30),
            "notion": CircuitBreakerConfig(failure_threshold=3, timeout=60),
            "stripe": CircuitBreakerConfig(failure_threshold=5, timeout=30),
            "openai": CircuitBreakerConfig(failure_threshold=3, timeout=120),
        }
    
    def get(self, name: str) -> CircuitBreaker:
        """Get or create a circuit breaker."""
        if name not in self._breakers:
            with self._lock:
                if name not in self._breakers:
                    config = self._configs.get(name)
                    self._breakers[name] = CircuitBreaker(name, config)
        return self._breakers[name]
    
    def get_all_states(self) -> Dict[str, Dict]:
        """Get state of all circuit breakers."""
        return {name: cb.get_state() for name, cb in self._breakers.items()}


# Global registry
circuit_breakers = CircuitBreakerRegistry()


def with_circuit_breaker(service_name: str):
    """
    Decorator to wrap a function with circuit breaker protection.
    
    Usage:
        @with_circuit_breaker("google")
        async def call_google_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            breaker = circuit_breakers.get(service_name)
            
            allowed, reason = breaker._should_attempt()
            if not allowed:
                raise CircuitBreakerOpen(reason)
            
            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure(e)
                raise
        
        def sync_wrapper(*args, **kwargs):
            breaker = circuit_breakers.get(service_name)
            
            allowed, reason = breaker._should_attempt()
            if not allowed:
                raise CircuitBreakerOpen(reason)
            
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure(e)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
