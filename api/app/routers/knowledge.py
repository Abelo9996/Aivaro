from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import KnowledgeEntry, User
from app.schemas import KnowledgeCreate, KnowledgeUpdate, KnowledgeResponse, VALID_CATEGORIES
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/categories")
async def list_categories():
    """List valid knowledge categories with descriptions."""
    descriptions = {
        "business_info": "Business name, what you do, location, hours of operation",
        "pricing": "Pricing, packages, discounts, deposit amounts",
        "policies": "Cancellation, refund, no-show, rescheduling policies",
        "contacts": "Key contacts, vendors, partners, team members",
        "deadlines": "Important dates, renewals, filings, milestones",
        "financials": "Revenue targets, costs, margins, budgets",
        "faq": "Common questions customers ask and how to answer them",
        "email_templates": "How to respond to specific types of emails",
        "custom": "Anything else Aivaro should know",
    }
    return [{"id": cat, "description": descriptions.get(cat, "")} for cat in VALID_CATEGORIES]


@router.get("/", response_model=List[KnowledgeResponse])
async def list_knowledge(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgeEntry).filter(KnowledgeEntry.user_id == current_user.id)
    if category:
        query = query.filter(KnowledgeEntry.category == category)
    entries = query.order_by(KnowledgeEntry.priority.desc(), KnowledgeEntry.updated_at.desc()).all()
    return [KnowledgeResponse.model_validate(e) for e in entries]


@router.post("/", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    data: KnowledgeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}")
    
    entry = KnowledgeEntry(
        user_id=current_user.id,
        category=data.category,
        title=data.title,
        content=data.content,
        priority=data.priority,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return KnowledgeResponse.model_validate(entry)


@router.put("/{entry_id}", response_model=KnowledgeResponse)
async def update_knowledge(
    entry_id: str,
    data: KnowledgeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = db.query(KnowledgeEntry).filter(
        KnowledgeEntry.id == entry_id,
        KnowledgeEntry.user_id == current_user.id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    if data.category is not None:
        if data.category not in VALID_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category.")
        entry.category = data.category
    if data.title is not None:
        entry.title = data.title
    if data.content is not None:
        entry.content = data.content
    if data.priority is not None:
        entry.priority = data.priority
    
    db.commit()
    db.refresh(entry)
    return KnowledgeResponse.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = db.query(KnowledgeEntry).filter(
        KnowledgeEntry.id == entry_id,
        KnowledgeEntry.user_id == current_user.id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    db.delete(entry)
    db.commit()
