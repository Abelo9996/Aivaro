from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class NodeSchema(BaseModel):
    id: str
    type: str
    label: str
    position: dict[str, float]
    parameters: dict[str, Any] = {}
    connectionId: Optional[str] = None
    requiresApproval: bool = False


class EdgeSchema(BaseModel):
    id: str
    source: str
    target: str


class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    summary: Optional[str] = None
    nodes: list[NodeSchema] = []
    edges: list[EdgeSchema] = []


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    nodes: Optional[list[NodeSchema]] = None
    edges: Optional[list[EdgeSchema]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    summary: Optional[str]
    nodes: list[dict]
    edges: list[dict]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
