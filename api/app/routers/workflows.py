from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Workflow, User
from app.schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workflows = db.query(Workflow).filter(Workflow.user_id == current_user.id, Workflow.is_agent_task == False).order_by(Workflow.updated_at.desc()).all()
    return [WorkflowResponse.model_validate(w) for w in workflows]


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workflow = Workflow(
        user_id=current_user.id,
        name=workflow_data.name,
        description=workflow_data.description,
        summary=workflow_data.summary,
        nodes=[n.model_dump() for n in workflow_data.nodes],
        edges=[e.model_dump() for e in workflow_data.edges]
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return WorkflowResponse.model_validate(workflow)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return WorkflowResponse.model_validate(workflow)


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    update_data: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    
    if "nodes" in update_dict and update_dict["nodes"] is not None:
        update_dict["nodes"] = [n.model_dump() if hasattr(n, 'model_dump') else n for n in update_dict["nodes"]]
    if "edges" in update_dict and update_dict["edges"] is not None:
        update_dict["edges"] = [e.model_dump() if hasattr(e, 'model_dump') else e for e in update_dict["edges"]]
    
    for field, value in update_dict.items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    
    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    db.delete(workflow)
    db.commit()
    
    return {"message": "Workflow deleted"}


@router.post("/poll-email-triggers")
async def poll_email_triggers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Poll Gmail for new emails and trigger matching workflows.
    Call this endpoint periodically (e.g., every minute) to check for new emails.
    """
    from app.services.email_trigger_service import EmailTriggerService
    
    service = EmailTriggerService()
    results = await service.poll_and_trigger(db, str(current_user.id))
    
    return {
        "triggered": len(results),
        "executions": results
    }

