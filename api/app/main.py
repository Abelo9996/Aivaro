from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import os

from app.routers import auth, workflows, executions, approvals, connections, templates, ai, chat
from app.database import engine, Base, SessionLocal
from app.models import user, workflow, execution, approval, connection, template
from app.config import settings

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

# Configure CORS - allow frontend URLs from environment
cors_origins = [
    "http://localhost:3000",
    "http://localhost:12001",
]

# Add production frontend URL from environment
frontend_url = os.getenv("FRONTEND_URL") or settings.frontend_url
if frontend_url and frontend_url not in cors_origins:
    cors_origins.append(frontend_url)
    # Also add without trailing slash and with trailing slash
    cors_origins.append(frontend_url.rstrip("/"))
    if not frontend_url.endswith("/"):
        cors_origins.append(frontend_url + "/")

# Add any additional allowed origins from environment (comma-separated)
additional_origins = os.getenv("ALLOWED_ORIGINS", "")
if additional_origins:
    for origin in additional_origins.split(","):
        origin = origin.strip()
        if origin and origin not in cors_origins:
            cors_origins.append(origin)

# Remove duplicates
cors_origins = list(set(cors_origins))

# Log CORS origins for debugging
print(f"[CORS] Allowed origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(executions.router, prefix="/api/executions", tags=["Run History"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(connections.router, prefix="/api/connections", tags=["Connections"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.get("/")
async def root():
    return {"message": "Welcome to Aivaro API", "docs": "/docs"}


@app.get("/health")
async def health():
    """Basic health check."""
    return {"status": "healthy"}


@app.get("/health/db")
async def health_db():
    """Health check with database connectivity verification."""
    from sqlalchemy import text
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
