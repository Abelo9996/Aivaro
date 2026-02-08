from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("executions.id"), nullable=False)
    node_id = Column(String, nullable=False)
    status = Column(String, default="pending")
    action_summary = Column(Text, nullable=True)
    action_details = Column(JSON, nullable=True)
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    execution = relationship("Execution", back_populates="approvals")
