from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ApprovalResponse(BaseModel):
    id: str
    execution_id: str
    node_id: str
    node_type: Optional[str] = None
    status: str
    action_summary: Optional[str] = None
    action_details: Optional[dict] = None
    # Frontend-compatible aliases
    message: Optional[str] = None
    action_data: Optional[dict] = None
    workflow_name: Optional[str] = None
    step_label: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApprovalAction(BaseModel):
    action: str
    rejection_reason: Optional[str] = None
