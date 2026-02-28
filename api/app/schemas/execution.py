from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class ExecutionCreate(BaseModel):
    workflow_id: str
    is_test: bool = False
    trigger_data: Optional[dict[str, Any]] = None


class ExecutionNodeResponse(BaseModel):
    id: str
    node_id: str
    node_type: str
    node_label: Optional[str]
    status: str
    input_data: Optional[dict]
    output_data: Optional[dict]
    logs: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    
    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    error: Optional[str] = None
    is_test: bool
    started_at: datetime
    completed_at: Optional[datetime]
    current_node_id: Optional[str]
    trigger_data: Optional[dict]
    execution_nodes: list[ExecutionNodeResponse] = []
    
    class Config:
        from_attributes = True
