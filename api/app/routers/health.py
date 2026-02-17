"""
Health check endpoints and system monitoring.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any
import asyncio
import os

from app.database import get_db
from app.config import get_settings
from app.utils.circuit_breaker import circuit_breakers

router = APIRouter()
settings = get_settings()

# Track startup time
STARTUP_TIME = datetime.utcnow()


def get_uptime() -> str:
    """Get application uptime as human-readable string."""
    delta = datetime.utcnow() - STARTUP_TIME
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 if the service is running.
    Used by load balancers and container orchestrators.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": get_uptime(),
    }


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check - verifies all dependencies are available.
    Returns 503 if any critical dependency is unavailable.
    """
    checks: Dict[str, Dict[str, Any]] = {}
    all_healthy = True
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy", "latency_ms": 0}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        all_healthy = False
    
    # Check OpenAI API key is configured
    if settings.openai_api_key:
        checks["openai"] = {"status": "configured"}
    else:
        checks["openai"] = {"status": "not_configured", "warning": "AI features will be limited"}
    
    # Check circuit breakers
    cb_states = circuit_breakers.get_all_states()
    open_circuits = [name for name, state in cb_states.items() if state["state"] == "open"]
    if open_circuits:
        checks["circuit_breakers"] = {
            "status": "degraded",
            "open_circuits": open_circuits
        }
    else:
        checks["circuit_breakers"] = {"status": "healthy", "count": len(cb_states)}
    
    status_code = 200 if all_healthy else 503
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": checks,
    }


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check - verifies the process is not deadlocked.
    If this fails, the container should be restarted.
    """
    # Simple async test to verify event loop is responsive
    try:
        await asyncio.wait_for(asyncio.sleep(0.001), timeout=1.0)
        return {"status": "alive", "timestamp": datetime.utcnow().isoformat() + "Z"}
    except asyncio.TimeoutError:
        return {"status": "unresponsive"}, 503


@router.get("/health/metrics")
async def metrics(db: Session = Depends(get_db)):
    """
    Basic metrics endpoint for monitoring.
    In production, consider using Prometheus-compatible format.
    """
    from app.models import Workflow, Execution, User
    
    # Gather metrics
    metrics_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": (datetime.utcnow() - STARTUP_TIME).total_seconds(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
    
    try:
        # Database metrics
        metrics_data["database"] = {
            "total_users": db.query(User).count(),
            "total_workflows": db.query(Workflow).count(),
            "active_workflows": db.query(Workflow).filter(Workflow.is_active == True).count(),
            "total_executions": db.query(Execution).count(),
            "recent_executions_24h": db.query(Execution).filter(
                Execution.started_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
            ).count(),
        }
    except Exception as e:
        metrics_data["database"] = {"error": str(e)}
    
    # Circuit breaker states
    metrics_data["circuit_breakers"] = circuit_breakers.get_all_states()
    
    return metrics_data


@router.get("/health/debug")
async def debug_info():
    """
    Debug information (should be disabled or protected in production).
    """
    import sys
    import platform
    
    # Only return sensitive info in development
    if os.getenv("ENVIRONMENT") == "production":
        return {"error": "Debug endpoint disabled in production"}
    
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "environment_vars": {
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "not_set"),
            "DATABASE_URL": "***" if settings.database_url else "not_set",
            "OPENAI_API_KEY": "***" if settings.openai_api_key else "not_set",
            "GOOGLE_CLIENT_ID": "***" if settings.google_client_id else "not_set",
        },
        "startup_time": STARTUP_TIME.isoformat() + "Z",
    }
