"""
Notification service for sending alerts to users.
Supports email notifications, in-app notifications, and webhooks.
"""
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_COMPLETED = "workflow_completed"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_TIMEOUT = "approval_timeout"
    CONNECTION_EXPIRED = "connection_expired"
    RATE_LIMIT_WARNING = "rate_limit_warning"
    SECURITY_ALERT = "security_alert"


@dataclass
class Notification:
    """Represents a notification to be sent."""
    type: NotificationType
    user_id: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: str = "normal"  # low, normal, high, urgent
    channels: List[str] = None  # email, in_app, webhook
    
    def __post_init__(self):
        if self.channels is None:
            self.channels = ["in_app"]


class NotificationService:
    """
    Service for sending notifications through various channels.
    
    In production, this would integrate with:
    - SendGrid/SES for email
    - Firebase/OneSignal for push
    - WebSocket for real-time in-app
    """
    
    # Notification templates
    TEMPLATES = {
        NotificationType.WORKFLOW_FAILED: {
            "title": "⚠️ Workflow Failed: {workflow_name}",
            "message": "Your workflow '{workflow_name}' failed during execution. Error: {error_message}",
            "priority": "high",
        },
        NotificationType.WORKFLOW_COMPLETED: {
            "title": "✅ Workflow Completed: {workflow_name}",
            "message": "Your workflow '{workflow_name}' completed successfully.",
            "priority": "low",
        },
        NotificationType.APPROVAL_REQUIRED: {
            "title": "🔔 Approval Required: {workflow_name}",
            "message": "Your workflow '{workflow_name}' is waiting for your approval at step '{step_name}'.",
            "priority": "high",
        },
        NotificationType.APPROVAL_TIMEOUT: {
            "title": "⏰ Approval Timed Out: {workflow_name}",
            "message": "The approval request for '{workflow_name}' at step '{step_name}' has expired.",
            "priority": "normal",
        },
        NotificationType.CONNECTION_EXPIRED: {
            "title": "🔗 Connection Expired: {service_name}",
            "message": "Your {service_name} connection has expired. Please re-authenticate to continue using it in workflows.",
            "priority": "high",
        },
        NotificationType.RATE_LIMIT_WARNING: {
            "title": "⚡ Rate Limit Warning",
            "message": "You're approaching your API rate limit for {service_name}. Consider spreading out your workflow executions.",
            "priority": "normal",
        },
        NotificationType.SECURITY_ALERT: {
            "title": "🚨 Security Alert",
            "message": "{message}",
            "priority": "urgent",
        },
    }
    
    def __init__(self, db_session=None):
        self.db = db_session
        self._email_enabled = False  # Would check for SendGrid/SES config
        self._push_enabled = False   # Would check for Firebase config
    
    async def send(self, notification: Notification) -> bool:
        """
        Send a notification through configured channels.
        
        Returns True if at least one channel succeeded.
        """
        results = []
        
        for channel in notification.channels:
            try:
                if channel == "email":
                    result = await self._send_email(notification)
                elif channel == "in_app":
                    result = await self._send_in_app(notification)
                elif channel == "webhook":
                    result = await self._send_webhook(notification)
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
                    result = False
                
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {e}")
                results.append(False)
        
        return any(results)
    
    async def notify_workflow_failed(
        self,
        user_id: str,
        workflow_name: str,
        workflow_id: str,
        error_message: str,
        execution_id: str,
    ) -> bool:
        """Send notification when a workflow fails."""
        template = self.TEMPLATES[NotificationType.WORKFLOW_FAILED]
        
        notification = Notification(
            type=NotificationType.WORKFLOW_FAILED,
            user_id=user_id,
            title=template["title"].format(workflow_name=workflow_name),
            message=template["message"].format(
                workflow_name=workflow_name,
                error_message=error_message[:200],
            ),
            data={
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "error": error_message,
            },
            priority=template["priority"],
            channels=["in_app", "email"],
        )
        
        return await self.send(notification)
    
    async def notify_approval_required(
        self,
        user_id: str,
        workflow_name: str,
        workflow_id: str,
        step_name: str,
        approval_id: str,
    ) -> bool:
        """Send notification when approval is required."""
        template = self.TEMPLATES[NotificationType.APPROVAL_REQUIRED]
        
        notification = Notification(
            type=NotificationType.APPROVAL_REQUIRED,
            user_id=user_id,
            title=template["title"].format(workflow_name=workflow_name),
            message=template["message"].format(
                workflow_name=workflow_name,
                step_name=step_name,
            ),
            data={
                "workflow_id": workflow_id,
                "approval_id": approval_id,
                "step_name": step_name,
            },
            priority=template["priority"],
            channels=["in_app", "email"],
        )
        
        return await self.send(notification)
    
    async def notify_connection_expired(
        self,
        user_id: str,
        service_name: str,
        connection_id: str,
    ) -> bool:
        """Send notification when a connection expires."""
        template = self.TEMPLATES[NotificationType.CONNECTION_EXPIRED]
        
        notification = Notification(
            type=NotificationType.CONNECTION_EXPIRED,
            user_id=user_id,
            title=template["title"].format(service_name=service_name),
            message=template["message"].format(service_name=service_name),
            data={
                "connection_id": connection_id,
                "service": service_name,
            },
            priority=template["priority"],
            channels=["in_app", "email"],
        )
        
        return await self.send(notification)
    
    async def _send_email(self, notification: Notification) -> bool:
        """Send notification via email."""
        if not self._email_enabled:
            logger.debug(f"Email not configured, skipping email for {notification.type}")
            return False
        
        # In production, integrate with SendGrid/SES
        # from sendgrid import SendGridAPIClient
        # ...
        
        logger.info(f"[Email] Would send to user {notification.user_id}: {notification.title}")
        return True
    
    async def _send_in_app(self, notification: Notification) -> bool:
        """Store notification for in-app display."""
        # In production, this would:
        # 1. Store in database
        # 2. Push via WebSocket for real-time
        
        logger.info(f"[InApp] Notification for user {notification.user_id}: {notification.title}")
        
        # Store in database if available
        if self.db:
            # Would create InAppNotification record
            pass
        
        return True
    
    async def _send_webhook(self, notification: Notification) -> bool:
        """Send notification via webhook."""
        # In production, send to user-configured webhook URL
        logger.info(f"[Webhook] Would send to user {notification.user_id}: {notification.title}")
        return True


# Global notification service instance
_notification_service: Optional[NotificationService] = None


def get_notification_service(db_session=None) -> NotificationService:
    """Get or create notification service instance."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService(db_session)
    return _notification_service
