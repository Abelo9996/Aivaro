"""
Email Trigger Service - Polls Gmail for new emails and triggers matching workflows.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Workflow, Execution, Connection
from app.services.integrations.google_service import GoogleService


class EmailTriggerService:
    """Service that polls for new emails and triggers workflows."""
    
    # Track processed message IDs to avoid duplicate triggers
    _processed_messages: set = set()
    
    @classmethod
    async def poll_and_trigger(cls, db: Session, user_id: Optional[str] = None) -> list[dict]:
        """
        Poll Gmail for new emails and trigger matching workflows.
        Returns list of triggered workflow executions.
        """
        results = []
        
        # Get all active workflows with email triggers
        query = db.query(Workflow).filter(Workflow.is_active == True)
        if user_id:
            query = query.filter(Workflow.user_id == user_id)
        
        workflows = query.all()
        
        for workflow in workflows:
            # Find email trigger nodes
            email_triggers = [
                node for node in workflow.nodes 
                if node.get("type") == "start_email"
            ]
            
            if not email_triggers:
                continue
            
            # Get user's Google connection
            connection = db.query(Connection).filter(
                Connection.user_id == workflow.user_id,
                Connection.type == "google",
                Connection.is_connected == True
            ).first()
            
            if not connection or not connection.credentials:
                continue
            
            # Check for new emails matching the trigger
            for trigger in email_triggers:
                try:
                    triggered = await cls._check_trigger(
                        db, workflow, trigger, connection.credentials
                    )
                    results.extend(triggered)
                except Exception as e:
                    print(f"Error checking email trigger for workflow {workflow.id}: {e}")
        
        return results
    
    @classmethod
    async def _check_trigger(
        cls, 
        db: Session, 
        workflow: Workflow, 
        trigger: dict, 
        credentials: dict
    ) -> list[dict]:
        """Check a single email trigger and execute workflow if matched."""
        results = []
        
        params = trigger.get("parameters", {})
        from_filter = params.get("from", "")
        subject_filter = params.get("subject", "")
        
        # Build Gmail query
        query_parts = ["is:unread"]
        if from_filter:
            query_parts.append(f"from:{from_filter}")
        if subject_filter:
            query_parts.append(f"subject:{subject_filter}")
        
        gmail_query = " ".join(query_parts)
        
        # Initialize Google service
        google = GoogleService(
            access_token=credentials.get("access_token"),
            refresh_token=credentials.get("refresh_token")
        )
        
        try:
            # Get recent unread messages
            messages = await google.list_messages(query=gmail_query, max_results=10)
            
            for msg_ref in messages:
                msg_id = msg_ref.get("id")
                
                # Skip already processed messages (check in-memory cache first)
                cache_key = f"{workflow.id}:{msg_id}"
                if cache_key in cls._processed_messages:
                    continue
                
                # Also check database for existing executions with this message_id
                existing = db.query(Execution).filter(
                    Execution.workflow_id == workflow.id
                ).all()
                
                already_processed = False
                for ex in existing:
                    if ex.trigger_data and ex.trigger_data.get("message_id") == msg_id:
                        already_processed = True
                        break
                
                if already_processed:
                    # Already processed - add to cache and skip
                    cls._processed_messages.add(cache_key)
                    continue
                
                # Get full message details
                message = await google.get_message(msg_id)
                
                # Extract email details
                headers = message.get("payload", {}).get("headers", [])
                email_data = cls._parse_email_headers(headers)
                email_data["message_id"] = msg_id
                email_data["snippet"] = message.get("snippet", "")
                
                # Create and run execution
                execution = Execution(
                    workflow_id=workflow.id,
                    status="running",
                    is_test=False,
                    started_at=datetime.utcnow(),
                    trigger_data=email_data
                )
                db.add(execution)
                db.commit()
                db.refresh(execution)
                
                # Run the workflow
                from app.services.workflow_runner import WorkflowRunner
                runner = WorkflowRunner(db, execution.id)
                runner.run(trigger_data=email_data)
                
                # Mark as processed
                cls._processed_messages.add(cache_key)
                
                # Limit cache size
                if len(cls._processed_messages) > 10000:
                    cls._processed_messages = set(list(cls._processed_messages)[-5000:])
                
                results.append({
                    "workflow_id": str(workflow.id),
                    "workflow_name": workflow.name,
                    "execution_id": str(execution.id),
                    "email_from": email_data.get("from"),
                    "email_subject": email_data.get("subject"),
                })
        
        finally:
            await google.close()
        
        return results
    
    @staticmethod
    def _parse_email_headers(headers: list) -> dict:
        """Parse email headers into a dict."""
        result = {}
        header_map = {
            "From": "from",
            "To": "to", 
            "Subject": "subject",
            "Date": "date",
        }
        
        for header in headers:
            name = header.get("name", "")
            value = header.get("value", "")
            if name in header_map:
                result[header_map[name]] = value
        
        return result


async def poll_email_triggers(user_id: Optional[str] = None) -> list[dict]:
    """Convenience function to poll email triggers."""
    db = SessionLocal()
    try:
        service = EmailTriggerService()
        return await service.poll_and_trigger(db, user_id)
    finally:
        db.close()
