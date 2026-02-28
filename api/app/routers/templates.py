from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
import re
import json
import copy

from app.database import get_db
from app.models import Template, Workflow, User
from app.schemas import TemplateResponse, WorkflowResponse
from app.routers.auth import get_current_user

router = APIRouter()

# Variables that are filled at runtime, not by the user during setup
RUNTIME_VARIABLES = {
    "today", "now", "timestamp", "date_now", "current_date", "current_time",
    "payment_link", "invoice_url", "invoice_link", "booking_link", "onboarding_link",
    "review_link", "tracking_link", "tracking_number", "confirmation_link",
    "ai_response", "ai_reply", "ai_summary",
    "from", "subject", "order_id",
}

# Map variable names to human-friendly labels and field types
FIELD_CONFIG = {
    "email": {"label": "Email Address", "type": "email", "placeholder": "customer@example.com"},
    "customer_email": {"label": "Customer Email", "type": "email", "placeholder": "customer@example.com"},
    "client_email": {"label": "Client Email", "type": "email", "placeholder": "client@example.com"},
    "name": {"label": "Customer Name", "type": "text", "placeholder": "John Smith"},
    "customer_name": {"label": "Customer Name", "type": "text", "placeholder": "John Smith"},
    "client_name": {"label": "Client Name", "type": "text", "placeholder": "John Smith"},
    "owner_name": {"label": "Your Name", "type": "text", "placeholder": "Your name"},
    "business_name": {"label": "Business Name", "type": "text", "placeholder": "Your business name"},
    "phone": {"label": "Phone Number", "type": "tel", "placeholder": "+1 (555) 000-0000"},
    "service": {"label": "Service Type", "type": "text", "placeholder": "e.g. Haircut, Consultation"},
    "location": {"label": "Location", "type": "text", "placeholder": "123 Main St"},
    "date": {"label": "Date", "type": "date", "placeholder": ""},
    "appointment_date": {"label": "Appointment Date", "type": "date", "placeholder": ""},
    "due_date": {"label": "Due Date", "type": "date", "placeholder": ""},
    "time": {"label": "Time", "type": "time", "placeholder": ""},
    "appointment_time": {"label": "Appointment Time", "type": "time", "placeholder": ""},
    "amount": {"label": "Amount ($)", "type": "number", "placeholder": "50.00"},
    "total": {"label": "Total ($)", "type": "number", "placeholder": "100.00"},
    "description": {"label": "Description", "type": "textarea", "placeholder": "Brief description..."},
    "package": {"label": "Package/Plan", "type": "text", "placeholder": "e.g. Basic, Premium"},
    "source": {"label": "Lead Source", "type": "text", "placeholder": "e.g. Website, Referral"},
    "shipping_address": {"label": "Shipping Address", "type": "textarea", "placeholder": "Full address"},
    "item": {"label": "Item", "type": "text", "placeholder": "Product or service name"},
    "customer": {"label": "Customer", "type": "text", "placeholder": "Customer name"},
    "payment_method": {"label": "Payment Method", "type": "text", "placeholder": "e.g. Card, Cash"},
}


def extract_setup_fields(nodes: list) -> list:
    """Extract user-configurable {{variables}} from template nodes."""
    all_text = json.dumps(nodes, default=str)
    variables = sorted(set(re.findall(r'\{\{(\w+)\}\}', all_text)))
    
    fields = []
    for var in variables:
        if var.lower() in RUNTIME_VARIABLES:
            continue
        config = FIELD_CONFIG.get(var, {})
        fields.append({
            "key": var,
            "label": config.get("label", var.replace("_", " ").title()),
            "type": config.get("type", "text"),
            "placeholder": config.get("placeholder", ""),
            "required": var in ("business_name", "email", "customer_email", "client_email", "name", "customer_name", "client_name"),
        })
    
    return fields


def interpolate_nodes(nodes: list, values: dict) -> list:
    """Replace {{variables}} in template nodes with user-provided values."""
    nodes_copy = copy.deepcopy(nodes)
    nodes_json = json.dumps(nodes_copy, default=str)
    for key, value in values.items():
        nodes_json = nodes_json.replace("{{" + key + "}}", str(value))
    return json.loads(nodes_json)


class UseTemplateRequest(BaseModel):
    values: Optional[Dict[str, str]] = None


@router.get("/")
async def list_templates(
    category: Optional[str] = None,
    business_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Template)
    
    if category:
        query = query.filter(Template.category == category)
    if business_type:
        templates = query.all()
        templates = [
            t for t in templates 
            if business_type.lower() in (t.business_types or [])
        ]
    else:
        templates = query.all()
    
    return [TemplateResponse.model_validate(t) for t in templates]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    template = db.query(Template).filter(Template.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateResponse.model_validate(template)


@router.get("/{template_id}/setup-fields")
async def get_template_setup_fields(
    template_id: str,
    db: Session = Depends(get_db)
):
    """Get the configurable fields for a template setup wizard."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    fields = extract_setup_fields(template.nodes or [])
    return {
        "template_id": template.id,
        "template_name": template.name,
        "fields": fields,
    }


@router.post("/{template_id}/use", response_model=WorkflowResponse)
async def use_template(
    template_id: str,
    request: UseTemplateRequest = UseTemplateRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check plan limits before creating workflow from template
    from app.services.plan_limits import check_can_create_workflow
    check_can_create_workflow(current_user, db)
    
    template = db.query(Template).filter(Template.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Interpolate user values into template nodes if provided
    nodes = template.nodes
    name = template.name
    if request.values:
        nodes = interpolate_nodes(nodes, request.values)
        # Customize workflow name if business_name provided
        if request.values.get("business_name"):
            name = f"{template.name} - {request.values['business_name']}"
    
    workflow = Workflow(
        user_id=current_user.id,
        name=name,
        description=template.description,
        summary=template.summary,
        nodes=nodes,
        edges=template.edges
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return WorkflowResponse.model_validate(workflow)
