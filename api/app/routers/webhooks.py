"""
Webhook Router - Handles incoming webhooks and form submissions to trigger workflows.

Each workflow with a start_form or start_webhook trigger gets a unique webhook URL.
External systems (Webflow, Typeform, custom forms) can POST to this URL to trigger the workflow.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, Any
import json
import hmac
import hashlib

from app.database import get_db
from app.models import Workflow, User
from app.services.workflow_runner import WorkflowRunner
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/trigger/{workflow_id}")
async def trigger_workflow_webhook(
    workflow_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Public webhook endpoint to trigger a workflow.
    
    Accepts JSON payload which becomes available as trigger data in the workflow.
    Can be called from any external form, webhook provider, or API.
    
    Example: POST /api/webhooks/trigger/abc123
    Body: {"name": "John", "email": "john@example.com", "message": "Hello!"}
    """
    # Find the workflow
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    if not workflow.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is not active"
        )
    
    # Check if workflow has a form or webhook trigger
    nodes = workflow.nodes or []
    has_valid_trigger = any(
        node.get("type") in ["start_form", "start_webhook"] 
        for node in nodes
    )
    
    if not has_valid_trigger:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow does not have a form or webhook trigger"
        )
    
    # Parse the incoming data
    try:
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            trigger_data = await request.json()
        elif "application/x-www-form-urlencoded" in content_type:
            form_data = await request.form()
            trigger_data = dict(form_data)
        elif "multipart/form-data" in content_type:
            form_data = await request.form()
            trigger_data = dict(form_data)
        else:
            # Try to parse as JSON anyway
            body = await request.body()
            if body:
                trigger_data = json.loads(body.decode())
            else:
                trigger_data = {}
    except Exception as e:
        trigger_data = {}
    
    # Add metadata
    trigger_data["_webhook"] = {
        "source_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "content_type": request.headers.get("content-type", "unknown"),
    }
    
    # Get the workflow owner
    owner = db.query(User).filter(User.id == workflow.user_id).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow owner not found"
        )
    
    # Run the workflow
    try:
        runner = WorkflowRunner(db, workflow, owner)
        execution = runner.run(trigger_data=trigger_data)
        
        return {
            "success": True,
            "message": "Workflow triggered successfully",
            "execution_id": execution.id,
            "status": execution.status,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger workflow: {str(e)}"
        )


@router.get("/url/{workflow_id}")
async def get_webhook_url(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """
    Get the webhook URL for a workflow.
    This URL can be used in external forms, Webflow, Typeform, etc.
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    api_url = settings.api_url or "http://localhost:8000"
    webhook_url = f"{api_url}/api/webhooks/trigger/{workflow_id}"
    
    return {
        "webhook_url": webhook_url,
        "method": "POST",
        "content_types": ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"],
        "example_curl": f'curl -X POST "{webhook_url}" -H "Content-Type: application/json" -d \'{{"name": "John", "email": "john@example.com"}}\'',
        "instructions": {
            "webflow": "Add this URL to your Webflow form's Action URL field",
            "typeform": "Use this URL in Typeform's webhook integration",
            "custom_html": f'<form action="{webhook_url}" method="POST">...</form>',
            "zapier": "Use this URL as a webhook destination in Zapier",
            "api": "POST JSON data to this URL from any API or script",
        }
    }


@router.post("/external/{provider}/{workflow_id}")
async def handle_external_webhook(
    provider: str,
    workflow_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handle webhooks from specific external providers with their own formats.
    Normalizes the data before triggering the workflow.
    
    Supported providers:
    - webflow: Webflow form submissions
    - typeform: Typeform responses
    - calendly: Calendly event notifications
    - stripe: Stripe webhook events
    - github: GitHub webhook events
    - shopify: Shopify webhook events
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    if not workflow.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is not active"
        )
    
    # Parse incoming data
    try:
        raw_data = await request.json()
    except:
        raw_data = {}
    
    # Normalize data based on provider
    trigger_data = _normalize_webhook_data(provider, raw_data, request.headers)
    
    # Get the workflow owner
    owner = db.query(User).filter(User.id == workflow.user_id).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow owner not found"
        )
    
    # Run the workflow
    try:
        runner = WorkflowRunner(db, workflow, owner)
        execution = runner.run(trigger_data=trigger_data)
        
        return {
            "success": True,
            "execution_id": execution.id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger workflow: {str(e)}"
        )


def _normalize_webhook_data(provider: str, data: dict, headers: Any) -> dict:
    """
    Normalize webhook data from different providers into a consistent format.
    """
    normalized = {
        "_provider": provider,
        "_raw": data,
    }
    
    if provider == "webflow":
        # Webflow form submissions come with a 'data' key
        form_data = data.get("data", data)
        normalized.update({
            "name": form_data.get("name", form_data.get("Name", "")),
            "email": form_data.get("email", form_data.get("Email", "")),
            "phone": form_data.get("phone", form_data.get("Phone", "")),
            "message": form_data.get("message", form_data.get("Message", "")),
            "form_name": data.get("name", "Webflow Form"),
            **form_data,
        })
    
    elif provider == "typeform":
        # Typeform responses
        form_response = data.get("form_response", {})
        answers = form_response.get("answers", [])
        for answer in answers:
            field_title = answer.get("field", {}).get("title", "field")
            field_key = field_title.lower().replace(" ", "_")
            
            # Get the answer value based on type
            answer_type = answer.get("type", "")
            if answer_type == "text":
                normalized[field_key] = answer.get("text", "")
            elif answer_type == "email":
                normalized[field_key] = answer.get("email", "")
                normalized["email"] = answer.get("email", "")
            elif answer_type == "phone_number":
                normalized[field_key] = answer.get("phone_number", "")
            elif answer_type == "choice":
                normalized[field_key] = answer.get("choice", {}).get("label", "")
            elif answer_type == "number":
                normalized[field_key] = answer.get("number", 0)
            else:
                normalized[field_key] = str(answer.get(answer_type, ""))
    
    elif provider == "calendly":
        # Calendly invitee events
        event_data = data.get("payload", {})
        invitee = event_data.get("invitee", {})
        event = event_data.get("event", {})
        
        normalized.update({
            "event_type": data.get("event", ""),
            "invitee_name": invitee.get("name", ""),
            "invitee_email": invitee.get("email", ""),
            "event_name": event.get("name", ""),
            "event_start_time": event.get("start_time", ""),
            "event_end_time": event.get("end_time", ""),
            "event_location": event.get("location", {}).get("location", ""),
            "name": invitee.get("name", ""),
            "email": invitee.get("email", ""),
        })
    
    elif provider == "stripe":
        # Stripe webhook events
        event_type = data.get("type", "")
        event_data = data.get("data", {}).get("object", {})
        
        normalized.update({
            "event_type": event_type,
            "customer_email": event_data.get("customer_email", event_data.get("email", "")),
            "customer_name": event_data.get("customer_name", event_data.get("name", "")),
            "amount": event_data.get("amount", 0) / 100 if event_data.get("amount") else 0,
            "currency": event_data.get("currency", "usd"),
            "status": event_data.get("status", ""),
            "stripe_id": event_data.get("id", ""),
            "email": event_data.get("customer_email", event_data.get("email", "")),
            "name": event_data.get("customer_name", event_data.get("name", "")),
        })
    
    elif provider == "github":
        # GitHub webhook events
        event_type = headers.get("x-github-event", "push")
        
        normalized.update({
            "event_type": event_type,
            "repository": data.get("repository", {}).get("full_name", ""),
            "sender": data.get("sender", {}).get("login", ""),
            "action": data.get("action", ""),
        })
        
        if event_type == "push":
            normalized["commits"] = len(data.get("commits", []))
            normalized["branch"] = data.get("ref", "").replace("refs/heads/", "")
        elif event_type == "pull_request":
            pr = data.get("pull_request", {})
            normalized["pr_title"] = pr.get("title", "")
            normalized["pr_number"] = pr.get("number", 0)
            normalized["pr_url"] = pr.get("html_url", "")
        elif event_type == "issues":
            issue = data.get("issue", {})
            normalized["issue_title"] = issue.get("title", "")
            normalized["issue_number"] = issue.get("number", 0)
            normalized["issue_url"] = issue.get("html_url", "")
    
    elif provider == "shopify":
        # Shopify webhook events
        normalized.update({
            "order_id": data.get("id", ""),
            "order_number": data.get("order_number", ""),
            "customer_email": data.get("email", ""),
            "customer_name": f"{data.get('customer', {}).get('first_name', '')} {data.get('customer', {}).get('last_name', '')}".strip(),
            "total_price": data.get("total_price", "0"),
            "currency": data.get("currency", "USD"),
            "email": data.get("email", ""),
            "name": f"{data.get('customer', {}).get('first_name', '')} {data.get('customer', {}).get('last_name', '')}".strip(),
        })
    
    else:
        # Generic: just flatten the data
        normalized.update(data)
    
    return normalized
