from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Execution(Base):
    __tablename__ = "executions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    status = Column(String, default="running")
    is_test = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    current_node_id = Column(String, nullable=True)
    trigger_data = Column(JSON, nullable=True)
    
    workflow = relationship("Workflow", back_populates="executions")
    execution_nodes = relationship("ExecutionNode", back_populates="execution", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="execution", cascade="all, delete-orphan")


class ExecutionNode(Base):
    __tablename__ = "execution_nodes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("executions.id"), nullable=False)
    node_id = Column(String, nullable=False)
    node_type = Column(String, nullable=False)
    node_label = Column(String, nullable=True)
    status = Column(String, default="pending")
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    logs = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    execution = relationship("Execution", back_populates="execution_nodes")
