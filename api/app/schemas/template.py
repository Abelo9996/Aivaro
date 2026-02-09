from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import Optional


class TemplateDefinition(BaseModel):
    nodes: list[dict] = []
    edges: list[dict] = []


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    summary: Optional[str]
    icon: Optional[str] = "⚡"
    category: Optional[str]
    business_types: list[str]
    nodes: list[dict]
    edges: list[dict]
    created_at: datetime
    
    @computed_field
    @property
    def definition(self) -> TemplateDefinition:
        return TemplateDefinition(nodes=self.nodes, edges=self.edges)
    
    class Config:
        from_attributes = True
