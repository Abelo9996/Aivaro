"""
Retry utilities with exponential backoff for resilient API calls.
"""
import asyncio
import functools
import random
from typing import Type, Tuple, Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RetryError(Exception):
    """Raised when all retry attempts fail."""
    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        super().__init__(message)
        self.last_exception = last_exception


def exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential calculation
        jitter: Add randomness to prevent thundering herd
        retryable_exceptions: Tuple of exception types that should trigger retry
        on_retry: Optional callback(attempt, exception, delay) called before each retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"[Retry] {func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise RetryError(
                            f"Function {func.__name__} failed after {max_retries + 1} attempts",
                            last_exception=e
                        )
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Add jitter (±25% randomness)
                    if jitter:
                        delay = delay * (0.75 + random.random() * 0.5)
                    
                    logger.warning(
                        f"[Retry] {func.__name__} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    if on_retry:
                        on_retry(attempt, e, delay)
                    
                    await asyncio.sleep(delay)
            
            return None  # Should never reach here
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            import time
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"[Retry] {func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise RetryError(
                            f"Function {func.__name__} failed after {max_retries + 1} attempts",
                            last_exception=e
                        )
                    
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    if jitter:
                        delay = delay * (0.75 + random.random() * 0.5)
                    
                    logger.warning(
                        f"[Retry] {func.__name__} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    if on_retry:
                        on_retry(attempt, e, delay)
                    
                    time.sleep(delay)
            
            return None
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Predefined retry decorators for common use cases
retry_api_call = exponential_backoff(
    max_retries=3,
    base_delay=1.0,
    retryable_exceptions=(ConnectionError, TimeoutError, OSError),
)

retry_database = exponential_backoff(
    max_retries=2,
    base_delay=0.5,
    max_delay=5.0,
    retryable_exceptions=(Exception,),  # Database-specific exceptions
)

retry_webhook = exponential_backoff(
    max_retries=5,
    base_delay=2.0,
    max_delay=300.0,  # 5 minutes max
    retryable_exceptions=(ConnectionError, TimeoutError),
)
