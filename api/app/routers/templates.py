from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Template, Workflow, User
from app.schemas import TemplateResponse, WorkflowResponse
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    category: Optional[str] = None,
    business_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Template)
    
    if category:
        query = query.filter(Template.category == category)
    
    templates = query.all()
    
    if business_type:
        templates = [
            t for t in templates 
            if not t.business_types or business_type in t.business_types
        ]
    
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


@router.post("/{template_id}/use", response_model=WorkflowResponse)
async def use_template(
    template_id: str,
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
    
    workflow = Workflow(
        user_id=current_user.id,
        name=template.name,
        description=template.description,
        summary=template.summary,
        nodes=template.nodes,
        edges=template.edges
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return WorkflowResponse.model_validate(workflow)
