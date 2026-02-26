"""
FastAPI middleware for request handling, logging, and rate limiting.
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import uuid
from typing import Callable
import logging

from app.utils.logging import set_correlation_id, set_user_id, get_correlation_id
from app.utils.rate_limit import rate_limiter, RateLimitExceeded

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request/response logging with correlation IDs.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip middleware for SSE streaming endpoints (BaseHTTPMiddleware breaks streaming)
        if "/stream" in request.url.path:
            return await call_next(request)

        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())[:8]
        set_correlation_id(correlation_id)
        
        # Extract user ID from auth token if present
        # This would typically come from the auth middleware
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            set_user_id(str(user_id))
        
        # Record start time
        start_time = time.time()
        
        # Log request
        logger.info(
            f"→ {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"✗ {request.method} {request.url.path} - Error: {e}",
                extra={"duration_ms": duration, "error": str(e)}
            )
            raise
        
        # Calculate duration
        duration = (time.time() - start_time) * 1000
        
        # Log response
        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            log_level,
            f"← {request.method} {request.url.path} {response.status_code} ({duration:.1f}ms)",
            extra={
                "status_code": response.status_code,
                "duration_ms": duration,
            }
        )
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Response-Time"] = f"{duration:.1f}ms"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API rate limiting.
    """
    
    # Paths that should be rate limited more strictly
    STRICT_PATHS = ["/api/ai/", "/api/workflows/run"]
    
    # Paths that are exempt from rate limiting
    EXEMPT_PATHS = ["/api/health", "/docs", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if "/stream" in request.url.path:
            return await call_next(request)
        path = request.url.path
        
        # Skip rate limiting for exempt paths
        if any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS):
            return await call_next(request)
        
        # Get rate limit key (use IP if not authenticated)
        user_id = getattr(request.state, "user_id", None)
        rate_key = f"user:{user_id}" if user_id else f"ip:{request.client.host if request.client else 'unknown'}"
        
        # Check rate limit
        allowed, retry_after = rate_limiter.check_limit(rate_key)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {rate_key}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "message": f"Too many requests. Please wait {retry_after:.0f} seconds.",
                },
                headers={"Retry-After": str(int(retry_after or 60))}
            )
        
        # Record the request
        rate_limiter.record_request(rate_key)
        
        try:
            response = await call_next(request)
            return response
        finally:
            # Release concurrent slot
            rate_limiter.release_request(rate_key)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if "/stream" in request.url.path:
            return await call_next(request)
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Only in production
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware.
    Catches unhandled exceptions and returns proper JSON responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if "/stream" in request.url.path:
            return await call_next(request)
        try:
            return await call_next(request)
        except RateLimitExceeded as e:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": str(e),
                    "retry_after": e.retry_after,
                },
                headers={"Retry-After": str(int(e.retry_after or 60))}
            )
        except Exception as e:
            correlation_id = get_correlation_id()
            logger.exception(f"Unhandled exception: {e}")
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "correlation_id": correlation_id,
                }
            )
