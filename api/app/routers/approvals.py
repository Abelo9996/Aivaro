from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Approval, Execution, Workflow, User
from app.schemas import ApprovalResponse, ApprovalAction
from app.routers.auth import get_current_user
from app.services.workflow_runner import WorkflowRunner

router = APIRouter()


@router.get("/", response_model=List[ApprovalResponse])
async def list_approvals(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Approval).join(Execution).join(Workflow).filter(
        Workflow.user_id == current_user.id
    )
    
    if status_filter:
        query = query.filter(Approval.status == status_filter)
    
    approvals = query.order_by(Approval.created_at.desc()).all()
    return [ApprovalResponse.model_validate(a) for a in approvals]


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(
    approval_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    approval = db.query(Approval).join(Execution).join(Workflow).filter(
        Approval.id == approval_id,
        Workflow.user_id == current_user.id
    ).first()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    return ApprovalResponse.model_validate(approval)


@router.post("/{approval_id}/action", response_model=ApprovalResponse)
async def action_approval(
    approval_id: str,
    action_data: ApprovalAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    approval = db.query(Approval).join(Execution).join(Workflow).filter(
        Approval.id == approval_id,
        Workflow.user_id == current_user.id
    ).first()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    if approval.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval has already been actioned"
        )
    
    if action_data.action == "approve":
        approval.status = "approved"
        approval.approved_by = current_user.id
        approval.approved_at = datetime.utcnow()
        db.commit()
        
        # Resume the workflow
        runner = WorkflowRunner(db, approval.execution_id)
        runner.resume_from_approval(approval_id)
        
    elif action_data.action == "reject":
        approval.status = "rejected"
        approval.rejection_reason = action_data.rejection_reason
        approval.approved_at = datetime.utcnow()
        
        # Mark execution as failed
        execution = db.query(Execution).filter(Execution.id == approval.execution_id).first()
        execution.status = "failed"
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Use 'approve' or 'reject'"
        )
    
    db.refresh(approval)
    return ApprovalResponse.model_validate(approval)
