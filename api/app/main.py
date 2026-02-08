from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, workflows, executions, approvals, connections, templates, ai
from app.database import engine, Base
from app.models import user, workflow, execution, approval, connection, template

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aivaro API",
    description="n8n, but built for non-technical founders",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(executions.router, prefix="/api/executions", tags=["Run History"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(connections.router, prefix="/api/connections", tags=["Connections"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])


@app.get("/")
async def root():
    return {"message": "Welcome to Aivaro API", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
