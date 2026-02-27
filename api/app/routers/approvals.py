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
    return [_enrich_approval(a, db) for a in approvals]


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
    
    return _enrich_approval(approval, db)


def _enrich_approval(approval: Approval, db: Session) -> ApprovalResponse:
    """Add workflow context, node type, and friendly labels to approval responses."""
    execution = approval.execution
    workflow = execution.workflow if execution else None
    
    # Find the node in the workflow to get type and label
    node_type = None
    step_label = None
    if workflow and workflow.nodes:
        for node in workflow.nodes:
            if node.get("id") == approval.node_id:
                node_type = node.get("type", "unknown")
                step_label = node.get("label", node_type)
                break
    
    # Build friendly node type label
    type_labels = {
        "send_email": "Send Email",
        "stripe_create_payment_link": "Create Payment Link",
        "stripe_create_invoice": "Create Invoice",
        "stripe_send_invoice": "Send Invoice",
        "twilio_send_sms": "Send SMS",
        "twilio_send_whatsapp": "Send WhatsApp",
        "twilio_make_call": "Make Phone Call",
        "mailchimp_send_campaign": "Send Campaign",
        "ai_reply": "AI Reply",
    }
    friendly_type = type_labels.get(node_type, step_label or node_type or "Action")
    
    return ApprovalResponse(
        id=approval.id,
        execution_id=approval.execution_id,
        node_id=approval.node_id,
        node_type=friendly_type,
        status=approval.status,
        action_summary=approval.action_summary,
        action_details=approval.action_details,
        message=approval.action_summary or f"Approve: {friendly_type}",
        action_data=approval.action_details,
        workflow_name=workflow.name if workflow else None,
        step_label=step_label,
        approved_at=approval.approved_at,
        rejection_reason=approval.rejection_reason,
        created_at=approval.created_at,
    )


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
