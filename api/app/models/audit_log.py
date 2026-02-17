"""
Audit log model for tracking user actions and system events.
Important for security, compliance, and debugging.
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.database import Base


class AuditLog(Base):
    """
    Audit log entry for tracking important actions.
    
    Use cases:
    - Security auditing (login attempts, API key usage)
    - Compliance (who changed what, when)
    - Debugging (tracing issues to root cause)
    - Analytics (user behavior patterns)
    """
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # When
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Who
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 can be up to 45 chars
    user_agent = Column(String(500), nullable=True)
    
    # What
    action = Column(String(100), nullable=False)  # e.g., "workflow.create", "user.login"
    resource_type = Column(String(50), nullable=True)  # e.g., "workflow", "connection"
    resource_id = Column(String(50), nullable=True)  # The ID of the affected resource
    
    # Details
    details = Column(JSONB, nullable=True)  # Additional context
    
    # Status
    status = Column(String(20), default="success")  # success, failure, pending
    error_message = Column(Text, nullable=True)
    
    # Correlation
    correlation_id = Column(String(50), nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_audit_logs_user_id_created_at", "user_id", "created_at"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id} at {self.created_at}>"
