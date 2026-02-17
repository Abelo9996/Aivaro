"""
Audit logging service for recording important events.
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import Request
import logging

from app.models.audit_log import AuditLog
from app.utils.logging import get_correlation_id

logger = logging.getLogger(__name__)


class AuditService:
    """Service for creating and querying audit logs."""
    
    # Define action categories
    ACTIONS = {
        # Authentication
        "user.login": "User logged in",
        "user.logout": "User logged out",
        "user.login_failed": "Login attempt failed",
        "user.password_reset": "Password reset requested",
        "user.register": "New user registered",
        
        # Workflows
        "workflow.create": "Workflow created",
        "workflow.update": "Workflow updated",
        "workflow.delete": "Workflow deleted",
        "workflow.activate": "Workflow activated",
        "workflow.deactivate": "Workflow deactivated",
        "workflow.execute": "Workflow executed",
        "workflow.execute_failed": "Workflow execution failed",
        
        # Connections
        "connection.create": "Connection created",
        "connection.delete": "Connection deleted",
        "connection.refresh": "Connection refreshed",
        
        # Approvals
        "approval.approve": "Approval granted",
        "approval.reject": "Approval rejected",
        
        # API
        "api_key.create": "API key created",
        "api_key.revoke": "API key revoked",
        
        # Webhooks
        "webhook.receive": "Webhook received",
        "webhook.process": "Webhook processed",
        
        # Security
        "security.rate_limit": "Rate limit exceeded",
        "security.invalid_token": "Invalid auth token used",
        "security.suspicious_activity": "Suspicious activity detected",
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def log(
        self,
        action: str,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            action: The action being logged (e.g., "workflow.create")
            user_id: ID of the user performing the action
            resource_type: Type of resource affected (e.g., "workflow")
            resource_id: ID of the affected resource
            details: Additional context as a dict
            status: "success", "failure", or "pending"
            error_message: Error message if status is "failure"
            request: FastAPI Request object for IP/user agent
        """
        # Extract request info
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent", "")[:500]
        
        # Create log entry
        log_entry = AuditLog(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details=details,
            status=status,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=get_correlation_id(),
        )
        
        self.db.add(log_entry)
        self.db.commit()
        
        # Also log to standard logger
        log_method = logger.warning if status == "failure" else logger.info
        log_method(f"[Audit] {action} by user {user_id}: {status}")
        
        return log_entry
    
    def log_success(
        self,
        action: str,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log a successful action."""
        return self.log(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            status="success",
            request=request,
        )
    
    def log_failure(
        self,
        action: str,
        error_message: str,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log a failed action."""
        return self.log(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            status="failure",
            error_message=error_message,
            request=request,
        )
    
    def get_user_activity(
        self,
        user_id: UUID,
        limit: int = 100,
        action_filter: Optional[str] = None,
    ) -> list[AuditLog]:
        """Get recent activity for a user."""
        query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        if action_filter:
            query = query.filter(AuditLog.action.like(f"{action_filter}%"))
        
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 50,
    ) -> list[AuditLog]:
        """Get audit history for a specific resource."""
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )


def audit_log(
    db: Session,
    action: str,
    **kwargs,
) -> AuditLog:
    """Convenience function for creating audit logs."""
    service = AuditService(db)
    return service.log(action=action, **kwargs)
