"""
Idempotency handling for webhook and API requests.
Prevents duplicate processing of the same request.
"""
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib
import json
import logging
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class IdempotencyRecord:
    """Record of a processed request."""
    key: str
    response: Any
    status_code: int
    created_at: datetime
    expires_at: datetime


class IdempotencyStore:
    """
    In-memory store for idempotency keys.
    
    In production, use Redis for distributed systems:
    - redis.setex(key, ttl, value)
    - redis.get(key)
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize the store.
        
        Args:
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.default_ttl = default_ttl
        self._store: Dict[str, IdempotencyRecord] = {}
        self._lock = Lock()
        self._last_cleanup = datetime.utcnow()
    
    def _cleanup_expired(self):
        """Remove expired records."""
        now = datetime.utcnow()
        
        # Only cleanup every 5 minutes
        if (now - self._last_cleanup).seconds < 300:
            return
        
        with self._lock:
            expired_keys = [
                key for key, record in self._store.items()
                if record.expires_at < now
            ]
            
            for key in expired_keys:
                del self._store[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired idempotency records")
            
            self._last_cleanup = now
    
    def get(self, key: str) -> Optional[IdempotencyRecord]:
        """Get a record by key if it exists and hasn't expired."""
        self._cleanup_expired()
        
        record = self._store.get(key)
        if record and record.expires_at > datetime.utcnow():
            return record
        return None
    
    def set(
        self,
        key: str,
        response: Any,
        status_code: int = 200,
        ttl: Optional[int] = None,
    ) -> IdempotencyRecord:
        """
        Store a response for an idempotency key.
        
        Args:
            key: The idempotency key
            response: The response to cache
            status_code: HTTP status code
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        ttl = ttl or self.default_ttl
        now = datetime.utcnow()
        
        record = IdempotencyRecord(
            key=key,
            response=response,
            status_code=status_code,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl),
        )
        
        with self._lock:
            self._store[key] = record
        
        return record
    
    def exists(self, key: str) -> bool:
        """Check if a key exists and is not expired."""
        return self.get(key) is not None


# Global idempotency store
idempotency_store = IdempotencyStore()


def generate_idempotency_key(
    user_id: str,
    action: str,
    payload: Optional[Dict] = None,
) -> str:
    """
    Generate an idempotency key for a request.
    
    Args:
        user_id: The user making the request
        action: The action being performed (e.g., "webhook:workflow_123")
        payload: Optional request payload to include in hash
    """
    key_parts = [user_id, action]
    
    if payload:
        # Sort keys for consistent hashing
        payload_str = json.dumps(payload, sort_keys=True)
        key_parts.append(payload_str)
    
    key_string = ":".join(key_parts)
    return hashlib.sha256(key_string.encode()).hexdigest()[:32]


def generate_webhook_idempotency_key(
    workflow_id: str,
    payload: Dict,
    timestamp: Optional[str] = None,
) -> str:
    """
    Generate idempotency key specifically for webhooks.
    
    Uses payload hash and optional timestamp to detect duplicates.
    """
    # Create a hash of the payload
    payload_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()[:16]
    
    key_parts = [f"webhook:{workflow_id}", payload_hash]
    
    # Include timestamp if provided (for services that include delivery time)
    if timestamp:
        key_parts.append(timestamp)
    
    return ":".join(key_parts)


class IdempotentOperation:
    """
    Context manager for idempotent operations.
    
    Usage:
        async with IdempotentOperation(key) as op:
            if op.cached:
                return op.cached_response
            
            result = await do_work()
            op.set_response(result)
            return result
    """
    
    def __init__(self, key: str, ttl: int = 3600):
        self.key = key
        self.ttl = ttl
        self.cached_record: Optional[IdempotencyRecord] = None
    
    @property
    def cached(self) -> bool:
        """Check if there's a cached response."""
        return self.cached_record is not None
    
    @property
    def cached_response(self) -> Any:
        """Get the cached response."""
        return self.cached_record.response if self.cached_record else None
    
    def __enter__(self):
        self.cached_record = idempotency_store.get(self.key)
        if self.cached_record:
            logger.info(f"[Idempotency] Returning cached response for key {self.key[:8]}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def __aenter__(self):
        return self.__enter__()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def set_response(self, response: Any, status_code: int = 200):
        """Cache the response for future requests."""
        idempotency_store.set(self.key, response, status_code, self.ttl)


def check_idempotency(key: str) -> Optional[Dict]:
    """
    Check if a request has already been processed.
    
    Returns the cached response if found, None otherwise.
    """
    record = idempotency_store.get(key)
    if record:
        return {
            "cached": True,
            "response": record.response,
            "status_code": record.status_code,
            "processed_at": record.created_at.isoformat(),
        }
    return None


def record_idempotency(key: str, response: Any, status_code: int = 200, ttl: int = 3600):
    """Record a response for idempotency."""
    idempotency_store.set(key, response, status_code, ttl)
