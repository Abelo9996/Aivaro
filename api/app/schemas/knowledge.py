from pydantic import BaseModel
from datetime import datetime
from typing import Optional


VALID_CATEGORIES = [
    "business_info",    # Business name, what you do, location, hours
    "pricing",          # Pricing, packages, discounts, deposits
    "policies",         # Cancellation, refund, no-show, rescheduling
    "contacts",         # Key contacts, vendors, partners
    "deadlines",        # Important dates, renewals, filings
    "financials",       # Revenue targets, costs, margins
    "faq",              # Common questions and answers
    "email_templates",  # How to respond to specific email types
    "custom",           # Anything else
]


class KnowledgeCreate(BaseModel):
    category: str
    title: str
    content: str
    priority: int = 0


class KnowledgeUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[int] = None


class KnowledgeResponse(BaseModel):
    id: str
    category: str
    title: str
    content: str
    priority: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
