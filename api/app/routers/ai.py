from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.services.ai_generator import (
    generate_workflow_from_prompt,
    generate_workflow_with_context,
    suggest_node_params,
    analyze_prompt_completeness
)

router = APIRouter()


class GenerateWorkflowRequest(BaseModel):
    prompt: str
    clarifications: Optional[Dict[str, Any]] = None
    skip_clarification: bool = False  # Force generation without clarifying


class ClarifyWorkflowRequest(BaseModel):
    prompt: str


class ClarificationQuestion(BaseModel):
    id: str
    question: str
    why: str
    options: Optional[List[str]] = None
    allow_multiple: bool = False


class ClarificationResponse(BaseModel):
    is_complete: bool
    confidence: int
    understood: Dict[str, Any]
    missing_info: List[str]
    questions: List[ClarificationQuestion]


class SuggestParamsRequest(BaseModel):
    node_type: str
    user_goal: str
    sample_data: Optional[dict] = None


@router.post("/clarify-workflow")
async def clarify_workflow(
    request: ClarifyWorkflowRequest,
    current_user: User = Depends(get_current_user)
) -> ClarificationResponse:
    """
    Analyze a workflow prompt and return clarifying questions if needed.
    
    This endpoint should be called BEFORE generate-workflow to ensure
    we have enough context to build a high-quality workflow.
    
    Returns:
    - is_complete: True if the prompt has enough detail
    - confidence: 0-100 score of how confident we are
    - understood: What we understood from the prompt
    - missing_info: What's unclear or missing
    - questions: Clarifying questions to ask the user
    """
    if not request.prompt or len(request.prompt.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="Please describe what you want to automate"
        )
    
    analysis = analyze_prompt_completeness(request.prompt)
    
    return ClarificationResponse(
        is_complete=analysis.get("is_complete", False),
        confidence=analysis.get("confidence", 50),
        understood=analysis.get("understood", {}),
        missing_info=analysis.get("missing_info", []),
        questions=[
            ClarificationQuestion(**q) for q in analysis.get("questions", [])
        ]
    )


@router.post("/generate-workflow")
async def generate_workflow(
    request: GenerateWorkflowRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a workflow from a prompt.
    
    For best results, call /clarify-workflow first and include the
    user's answers in the clarifications field.
    
    Args:
    - prompt: Description of the workflow to create
    - clarifications: Dict of question_id -> answer from clarifying questions
    - skip_clarification: Set to True to force generation without clarifying
    """
    if not request.prompt or len(request.prompt.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Please provide a more detailed description of what you want to automate"
        )
    
    # If clarifications provided, use them
    if request.clarifications:
        result = generate_workflow_with_context(request.prompt, request.clarifications)
    # If not skipping clarification, check if we should ask questions
    elif not request.skip_clarification:
        analysis = analyze_prompt_completeness(request.prompt)
        
        # If confidence is too low, return questions instead of generating
        if analysis.get("confidence", 0) < 60 and analysis.get("questions"):
            return {
                "needs_clarification": True,
                "message": "I'd like to ask a few questions to make sure I build exactly what you need.",
                "understood": analysis.get("understood", {}),
                "questions": analysis.get("questions", [])
            }
        
        # Confidence is high enough, generate
        result = generate_workflow_from_prompt(request.prompt)
    else:
        # Skip clarification, just generate
        result = generate_workflow_from_prompt(request.prompt)
    
    # Add flag to indicate this is a complete workflow
    result["needs_clarification"] = False
    return result


@router.post("/suggest-node-params")
async def suggest_params(
    request: SuggestParamsRequest,
    current_user: User = Depends(get_current_user)
):
    result = suggest_node_params(
        request.node_type,
        request.user_goal,
        request.sample_data
    )
    return {"suggested_parameters": result}
