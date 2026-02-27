"""
Chat API Router — Conversations, streaming, history
"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Execution, Workflow, User
from app.models.chat import ChatMessage as ChatMessageModel, ChatConversation
from app.routers.auth import get_current_user
from app.services.chat_service import chat_about_execution
from app.services.agentic_chat import agentic_chat, agentic_chat_stream
from app.services.agent_executor import run_agent_task

router = APIRouter()


class ChatMessageSchema(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    history: Optional[List[ChatMessageSchema]] = None

class ChatResponse(BaseModel):
    response: str
    context_type: str
    conversation_id: str


# --- Conversations ---

@router.get("/conversations")
async def list_conversations(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's conversations, most recent first."""
    convos = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == current_user.id, ChatConversation.is_archived == False)
        .order_by(ChatConversation.updated_at.desc())
        .limit(limit)
        .all()
    )
    result = []
    for c in convos:
        # Get message count and last message preview
        msgs = (
            db.query(ChatMessageModel)
            .filter(ChatMessageModel.conversation_id == c.id)
            .order_by(ChatMessageModel.created_at.desc())
            .limit(1)
            .all()
        )
        last_msg = msgs[0] if msgs else None
        msg_count = db.query(ChatMessageModel).filter(ChatMessageModel.conversation_id == c.id).count()
        result.append({
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
            "message_count": msg_count,
            "last_message": last_msg.content[:100] if last_msg else None,
            "last_role": last_msg.role if last_msg else None,
        })
    return result


@router.post("/conversations")
async def create_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    convo = ChatConversation(user_id=current_user.id, title="New conversation")
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return {"id": convo.id, "title": convo.title, "created_at": convo.created_at.isoformat()}


@router.patch("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    title: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    convo = db.query(ChatConversation).filter(
        ChatConversation.id == conversation_id, ChatConversation.user_id == current_user.id
    ).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    convo.title = title
    db.commit()
    return {"id": convo.id, "title": convo.title}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    convo = db.query(ChatConversation).filter(
        ChatConversation.id == conversation_id, ChatConversation.user_id == current_user.id
    ).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    convo.is_archived = True
    db.commit()
    return {"status": "archived"}


# --- Messages ---

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a conversation with full metadata."""
    convo = db.query(ChatConversation).filter(
        ChatConversation.id == conversation_id, ChatConversation.user_id == current_user.id
    ).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = (
        db.query(ChatMessageModel)
        .filter(ChatMessageModel.conversation_id == conversation_id)
        .order_by(ChatMessageModel.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "metadata": m.metadata_json,
            "timestamp": m.created_at.isoformat(),
        }
        for m in messages
    ]


# --- Streaming Chat ---

@router.post("/assistant/stream")
async def chat_assistant_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """SSE streaming endpoint — auto-creates conversation if none provided."""
    convo_id = request.conversation_id

    # Auto-create conversation if needed
    if not convo_id:
        convo = ChatConversation(user_id=current_user.id, title="New conversation")
        db.add(convo)
        db.commit()
        db.refresh(convo)
        convo_id = convo.id
    else:
        convo = db.query(ChatConversation).filter(
            ChatConversation.id == convo_id, ChatConversation.user_id == current_user.id
        ).first()
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")

    async def event_stream():
        # Send conversation_id first so frontend can track it
        yield f"data: {json.dumps({'type': 'conversation', 'conversation_id': convo_id})}\n\n"

        async for event in agentic_chat_stream(
            user=current_user, db=db, user_message=request.message, conversation_id=convo_id
        ):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# --- Non-streaming fallback ---

@router.post("/assistant", response_model=ChatResponse)
async def chat_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    convo_id = request.conversation_id
    if not convo_id:
        convo = ChatConversation(user_id=current_user.id, title="New conversation")
        db.add(convo)
        db.commit()
        db.refresh(convo)
        convo_id = convo.id
    response = await agentic_chat(user=current_user, db=db, user_message=request.message, conversation_id=convo_id)
    return ChatResponse(response=response, context_type="global", conversation_id=convo_id)


# --- Agent Execution SSE endpoint ---

class AgentTaskRequest(BaseModel):
    goal: str
    context: Optional[dict] = None
    is_test: Optional[bool] = False

@router.post("/agent/run")
async def run_agent(
    request: AgentTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SSE endpoint for running an agent task directly.
    Streams real-time events as the agent thinks and acts.
    """
    async def event_stream():
        async for event in run_agent_task(
            db=db,
            user=current_user,
            goal=request.goal,
            context=request.context,
            is_test=request.is_test or False,
        ):
            yield f"data: {json.dumps(event)}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# --- Legacy endpoints (backwards compat) ---

@router.get("/history")
async def get_chat_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Legacy: return recent messages across all conversations."""
    messages = (
        db.query(ChatMessageModel)
        .filter(ChatMessageModel.user_id == current_user.id)
        .order_by(ChatMessageModel.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    return [
        {
            "role": m.role, "content": m.content,
            "metadata": m.metadata_json,
            "timestamp": m.created_at.isoformat(),
            "conversation_id": m.conversation_id,
        }
        for m in messages
    ]


@router.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(ChatMessageModel).filter(ChatMessageModel.user_id == current_user.id).delete()
    db.query(ChatConversation).filter(ChatConversation.user_id == current_user.id).delete()
    db.commit()
    return {"status": "cleared"}


# --- Execution chat ---

class ExecChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessageSchema]] = None

@router.post("/execution/{execution_id}")
async def chat_execution(
    execution_id: str,
    request: ExecChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    workflow = db.query(Workflow).filter(Workflow.id == execution.workflow_id).first()
    if not workflow or workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    history = [{"role": m.role, "content": m.content} for m in request.history] if request.history else None
    response = await chat_about_execution(execution=execution, workflow=workflow, user_message=request.message, chat_history=history)
    return {"response": response, "context_type": "execution"}
