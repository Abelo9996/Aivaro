from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ApprovalResponse(BaseModel):
    id: str
    execution_id: str
    node_id: str
    status: str
    action_summary: Optional[str]
    action_details: Optional[dict]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApprovalAction(BaseModel):
    action: str
    rejection_reason: Optional[str] = None
