"""
Chat API Router
Provides endpoints for:
1. Execution-specific chat - discuss results of a workflow run
2. Global AI assistant - company-wide context assistant
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db
from app.models import Execution, Workflow, User
from app.routers.auth import get_current_user
from app.services.chat_service import chat_about_execution, chat_global_assistant

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str
    context_type: str  # "execution" or "global"


@router.post("/execution/{execution_id}", response_model=ChatResponse)
async def chat_execution(
    execution_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat about a specific workflow execution.
    The AI has context about the workflow, its steps, and execution results.
    """
    # Get execution
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    # Get workflow
    workflow = db.query(Workflow).filter(Workflow.id == execution.workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Verify ownership
    if workflow.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this execution"
        )
    
    # Convert history to list of dicts
    history = None
    if request.history:
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
    
    # Get AI response
    response = await chat_about_execution(
        execution=execution,
        workflow=workflow,
        user_message=request.message,
        chat_history=history
    )
    
    return ChatResponse(
        response=response,
        context_type="execution"
    )


@router.post("/assistant", response_model=ChatResponse)
async def chat_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with the global AI assistant.
    The AI has context about all workflows, executions, and company information.
    """
    # Convert history to list of dicts
    history = None
    if request.history:
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
    
    # Get AI response
    response = await chat_global_assistant(
        user=current_user,
        db=db,
        user_message=request.message,
        chat_history=history
    )
    
    return ChatResponse(
        response=response,
        context_type="global"
    )


@router.get("/assistant/context")
async def get_assistant_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of what context the assistant has access to.
    Useful for displaying to users what the AI knows about.
    """
    from app.services.chat_service import build_global_context
    
    workflows = db.query(Workflow).filter(Workflow.user_id == current_user.id).count()
    executions = db.query(Execution).join(Workflow).filter(
        Workflow.user_id == current_user.id
    ).count()
    
    return {
        "context_summary": {
            "workflows_count": workflows,
            "executions_count": executions,
            "user_name": current_user.full_name or current_user.email,
            "business_type": current_user.business_type,
        },
        "capabilities": [
            "Answer questions about any workflow",
            "Analyze execution results and patterns",
            "Suggest workflow improvements",
            "Help troubleshoot issues",
            "Recommend new automations"
        ]
    }
