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

# Variables that are filled at runtime from trigger data, not by the user during setup
RUNTIME_VARIABLES = {
    "today", "now", "timestamp", "date_now", "current_date", "current_time",
    "payment_link", "invoice_url", "invoice_link", "booking_link", "onboarding_link",
    "review_link", "tracking_link", "tracking_number", "confirmation_link",
    "ai_response", "ai_reply", "ai_summary",
    "from", "subject", "order_id",
}

# Node parameters that users should configure during setup, keyed by node_type
# Each entry: param_key -> {label, type, placeholder, required, group}
NODE_SETUP_PARAMS = {
    "append_row": {
        "spreadsheet": {"label": "Spreadsheet Name or URL", "type": "text", "placeholder": "e.g. My Bookings Sheet", "required": True},
        "sheet_name": {"label": "Sheet/Tab Name", "type": "text", "placeholder": "Sheet1", "required": False},
    },
    "stripe_create_payment_link": {
        "amount": {"label": "Payment Amount ($)", "type": "number", "placeholder": "50.00", "required": True},
        "product_name": {"label": "Product/Service Name", "type": "text", "placeholder": "Booking Deposit", "required": False},
    },
    "stripe_create_invoice": {
        "amount": {"label": "Invoice Amount ($)", "type": "number", "placeholder": "100.00", "required": True},
        "due_days": {"label": "Days Until Due", "type": "number", "placeholder": "30", "required": False},
        "auto_send": {"label": "Auto-send to Customer?", "type": "select", "options": ["true", "false"], "placeholder": "", "required": False},
    },
    "google_calendar_create": {
        "duration": {"label": "Event Duration (hours)", "type": "number", "placeholder": "1", "required": False},
        "location": {"label": "Default Location", "type": "text", "placeholder": "123 Main St", "required": False},
    },
    "ai_reply": {
        "tone": {"label": "Reply Tone", "type": "select", "options": ["professional", "friendly", "casual", "formal"], "placeholder": "", "required": False},
        "context": {"label": "Business Context for AI", "type": "textarea", "placeholder": "Describe your business so the AI can write better replies...", "required": False},
    },
    "delay": {
        "duration": {"label": "Wait Duration", "type": "number", "placeholder": "1", "required": False},
        "unit": {"label": "Time Unit", "type": "select", "options": ["minutes", "hours", "days"], "placeholder": "", "required": False},
    },
}


def extract_setup_fields(nodes: list) -> list:
    """Extract user-configurable fields from template nodes.
    
    Two types of fields:
    1. Node config params (spreadsheet name, payment amount, etc.)
    2. Business info {{variables}} used across nodes (business_name, etc.)
    """
    fields = []
    seen_params = set()  # Avoid duplicate fields for same param across nodes
    
    # 1. Extract node-level config params
    for node in nodes:
        node_type = node.get("type", "")
        if node_type.startswith("start"):
            continue
        
        param_config = NODE_SETUP_PARAMS.get(node_type, {})
        if not param_config:
            continue
            
        node_label = node.get("label", node_type)
        node_params = node.get("parameters", {})
        
        for param_key, config in param_config.items():
            if param_key in seen_params:
                # For duplicate params (e.g. multiple append_row nodes), make unique
                field_key = f"{node.get('id', node_type)}__{param_key}"
            else:
                field_key = f"{node_type}__{param_key}"
                seen_params.add(param_key)
            
            current_value = str(node_params.get(param_key, ""))
            # Skip if the current value contains {{variables}} — it's runtime-filled
            if "{{" in current_value and "}}" in current_value:
                continue
                
            fields.append({
                "key": field_key,
                "node_id": node.get("id", ""),
                "node_type": node_type,
                "node_label": node_label,
                "param_key": param_key,
                "label": config["label"],
                "type": config["type"],
                "placeholder": config.get("placeholder", ""),
                "required": config.get("required", False),
                "options": config.get("options"),
                "current_value": current_value if current_value and "{{" not in current_value else "",
            })
    
    # 2. Extract business-level {{variables}} that appear in non-runtime contexts
    all_text = json.dumps(nodes, default=str)
    variables = sorted(set(re.findall(r'\{\{(\w+)\}\}', all_text)))
    
    BUSINESS_VAR_CONFIG = {
        "business_name": {"label": "Business Name", "type": "text", "placeholder": "Your business name"},
        "owner_name": {"label": "Your Name", "type": "text", "placeholder": "Your name"},
    }
    
    business_vars = {"business_name", "owner_name"}
    for var in variables:
        if var.lower() in RUNTIME_VARIABLES or var not in business_vars:
            continue
        config = BUSINESS_VAR_CONFIG.get(var, {})
        fields.insert(0, {  # Business info at the top
            "key": f"var__{var}",
            "node_id": None,
            "node_type": None,
            "node_label": None,
            "param_key": var,
            "label": config.get("label", var.replace("_", " ").title()),
            "type": config.get("type", "text"),
            "placeholder": config.get("placeholder", ""),
            "required": var == "business_name",
            "options": None,
            "current_value": "",
        })
    
    return fields


def interpolate_nodes(nodes: list, field_values: dict, fields_meta: list) -> list:
    """Apply setup wizard values to template nodes."""
    nodes_copy = copy.deepcopy(nodes)
    
    # Build lookup: field_key -> (node_id, param_key, value)
    field_lookup = {f["key"]: f for f in fields_meta}
    
    # Apply node-specific param values
    for field_key, value in field_values.items():
        if not value:
            continue
        meta = field_lookup.get(field_key)
        if not meta:
            continue
        
        if meta.get("node_id"):
            # Node-level param — set directly on the matching node
            for node in nodes_copy:
                if node.get("id") == meta["node_id"]:
                    if "parameters" not in node:
                        node["parameters"] = {}
                    node["parameters"][meta["param_key"]] = value
                    break
        else:
            # Business-level variable — replace {{var}} across all nodes
            var_name = meta["param_key"]
            nodes_json = json.dumps(nodes_copy, default=str)
            nodes_json = nodes_json.replace("{{" + var_name + "}}", value)
            nodes_copy = json.loads(nodes_json)
    
    return nodes_copy


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
        fields_meta = extract_setup_fields(template.nodes or [])
        nodes = interpolate_nodes(nodes, request.values, fields_meta)
        # Customize workflow name if business_name provided
        biz_name = request.values.get("var__business_name", "")
        if biz_name:
            name = f"{template.name} - {biz_name}"
    
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
