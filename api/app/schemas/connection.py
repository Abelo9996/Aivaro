from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ConnectionCreate(BaseModel):
    name: str
    type: str
    credentials: Optional[dict] = None


class ConnectionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    type: str
    is_connected: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
