from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import os
import logging

from app.routers import auth, workflows, executions, approvals, connections, templates, ai, chat, webhooks, knowledge
from app.routers import health
from app.database import engine, Base, SessionLocal
from app.models import user, workflow, execution, approval, connection, template, knowledge as knowledge_model
from app.config import settings
from app.utils.logging import setup_logging
from app.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    ErrorHandlingMiddleware,
)

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
json_logs = os.getenv("ENVIRONMENT") == "production"
setup_logging(level=log_level, json_format=json_logs)

logger = logging.getLogger(__name__)

# Create all tables
Base.metadata.create_all(bind=engine)

# Background task for email polling
async def poll_email_triggers_task():
    """Background task that polls for email triggers every 60 seconds."""
    from app.services.email_trigger_service import EmailTriggerService
    
    while True:
        try:
            db = SessionLocal()
            service = EmailTriggerService()
            results = await service.poll_and_trigger(db)
            if results:
                print(f"[Email Trigger] Triggered {len(results)} workflow(s)")
            db.close()
        except Exception as e:
            print(f"[Email Trigger] Error: {e}")
        
        await asyncio.sleep(60)  # Poll every 60 seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Start background email polling task
    task = asyncio.create_task(poll_email_triggers_task())
    print("[Email Trigger] Background polling started (every 60 seconds)")
    yield
    # Cleanup on shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Aivaro API",
    description="n8n, but built for non-technical founders",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - be permissive for now to debug
# In production, you should restrict this to specific origins
cors_origins = [
    "http://localhost:3000",
    "http://localhost:12001",
]

# Add production frontend URL from environment
frontend_url = os.getenv("FRONTEND_URL", "").strip()
if frontend_url:
    # Add both with and without www
    cors_origins.append(frontend_url)
    cors_origins.append(frontend_url.rstrip("/"))
    # If it has www, also add without www and vice versa
    if "://www." in frontend_url:
        cors_origins.append(frontend_url.replace("://www.", "://"))
    elif "://" in frontend_url and "://www." not in frontend_url:
        cors_origins.append(frontend_url.replace("://", "://www."))

# Add any additional allowed origins from environment (comma-separated)
additional_origins = os.getenv("ALLOWED_ORIGINS", "")
if additional_origins:
    for origin in additional_origins.split(","):
        origin = origin.strip()
        if origin:
            cors_origins.append(origin)

# Remove duplicates and empty strings
cors_origins = list(set([o for o in cors_origins if o]))

# Log CORS origins for debugging
logger.info(f"[CORS] Allowed origins: {cors_origins}")

# Add middleware (order matters - first added = last executed)
# NOTE: BaseHTTPMiddleware breaks SSE streaming - disabled for now
# app.add_middleware(ErrorHandlingMiddleware)
# app.add_middleware(SecurityHeadersMiddleware)
# app.add_middleware(RequestLoggingMiddleware)

# CORS must be after custom middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Response-Time"],
)

# Health check routes (no auth required)
app.include_router(health.router, prefix="/api/health", tags=["Health"])

# API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(executions.router, prefix="/api/executions", tags=["Run History"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(connections.router, prefix="/api/connections", tags=["Connections"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge Base"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Aivaro API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health/ready",
    }
