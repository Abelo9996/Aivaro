from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.services.ai_generator import generate_workflow_from_prompt, suggest_node_params

router = APIRouter()


class GenerateWorkflowRequest(BaseModel):
    prompt: str


class SuggestParamsRequest(BaseModel):
    node_type: str
    user_goal: str
    sample_data: Optional[dict] = None


@router.post("/generate-workflow")
async def generate_workflow(
    request: GenerateWorkflowRequest,
    current_user: User = Depends(get_current_user)
):
    if not request.prompt or len(request.prompt.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Please provide a more detailed description of what you want to automate"
        )
    
    result = generate_workflow_from_prompt(request.prompt)
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
