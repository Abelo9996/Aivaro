"""
Structured logging with correlation IDs for request tracing.
"""
import logging
import json
import sys
import uuid
from typing import Optional, Any, Dict
from contextvars import ContextVar
from datetime import datetime
from functools import wraps

# Context variable for correlation ID (thread/async safe)
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def get_correlation_id() -> str:
    """Get current correlation ID or generate one."""
    cid = correlation_id_var.get()
    if not cid:
        cid = str(uuid.uuid4())[:8]
        correlation_id_var.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """Set correlation ID for current context."""
    correlation_id_var.set(cid)


def set_user_id(uid: str) -> None:
    """Set user ID for current context."""
    user_id_var.set(uid)


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Includes correlation ID, timestamp, and context.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": correlation_id_var.get() or "none",
        }
        
        # Add user ID if available
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


class ConsoleFormatter(logging.Formatter):
    """
    Pretty console formatter for development.
    """
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        cid = correlation_id_var.get() or "----"
        user_id = user_id_var.get()
        
        # Build prefix
        prefix = f"[{cid}]"
        if user_id:
            prefix += f"[user:{user_id[:8]}]"
        
        # Format message
        message = f"{color}{record.levelname:7}{self.RESET} {prefix} {record.getMessage()}"
        
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)
        
        return message


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    include_libs: bool = False
) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_format: Use JSON format (for production)
        include_libs: Include logs from third-party libraries
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    if json_format:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(ConsoleFormatter())
    
    root_logger.addHandler(handler)
    
    # Quiet noisy libraries unless explicitly included
    if not include_libs:
        for lib in ["urllib3", "httpx", "httpcore", "asyncio", "sqlalchemy"]:
            logging.getLogger(lib).setLevel(logging.WARNING)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that includes correlation ID and extra context.
    """
    
    def process(self, msg: str, kwargs: Dict) -> tuple:
        # Add extra data to the record
        extra = kwargs.get("extra", {})
        extra["correlation_id"] = get_correlation_id()
        
        user_id = user_id_var.get()
        if user_id:
            extra["user_id"] = user_id
        
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(name: str) -> LoggerAdapter:
    """Get a logger with context support."""
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, {})


# Convenience function for logging with extra data
def log_event(
    logger: logging.Logger,
    level: str,
    message: str,
    **extra_data: Any
) -> None:
    """Log an event with extra structured data."""
    record = logger.makeRecord(
        logger.name,
        getattr(logging, level.upper()),
        "",
        0,
        message,
        (),
        None
    )
    record.extra_data = extra_data
    logger.handle(record)


# Decorator for logging function execution
def log_execution(logger_name: str = "aivaro"):
    """Decorator to log function entry and exit."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            func_name = func.__name__
            
            logger.debug(f"Entering {func_name}")
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"Completed {func_name}")
                return result
            except Exception as e:
                logger.error(f"Failed {func_name}: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            func_name = func.__name__
            
            logger.debug(f"Entering {func_name}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func_name}")
                return result
            except Exception as e:
                logger.error(f"Failed {func_name}: {e}")
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
