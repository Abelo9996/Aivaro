from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TemplateResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    summary: Optional[str]
    category: Optional[str]
    business_types: list[str]
    nodes: list[dict]
    edges: list[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True
