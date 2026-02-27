"""Knowledge base service — builds context strings for AI consumption."""
from sqlalchemy.orm import Session
from app.models import KnowledgeEntry

CATEGORY_LABELS = {
    "business_info": "Business Information",
    "pricing": "Pricing & Packages",
    "policies": "Policies",
    "contacts": "Key Contacts",
    "deadlines": "Important Deadlines",
    "financials": "Financial Info",
    "faq": "FAQ",
    "email_templates": "Email Response Guidelines",
    "custom": "Other",
}


def get_knowledge_context(user_id: str, db: Session, max_chars: int = 4000) -> str:
    """Build a knowledge context string for injection into AI prompts.
    
    Returns empty string if no knowledge entries exist.
    Entries are ordered by priority (high first), then grouped by category.
    """
    entries = db.query(KnowledgeEntry).filter(
        KnowledgeEntry.user_id == user_id
    ).order_by(
        KnowledgeEntry.priority.desc(),
        KnowledgeEntry.category,
        KnowledgeEntry.updated_at.desc(),
    ).all()
    
    if not entries:
        return ""
    
    # Group by category
    grouped = {}
    for e in entries:
        grouped.setdefault(e.category, []).append(e)
    
    lines = ["BUSINESS KNOWLEDGE BASE (use this context when responding, creating workflows, and replying to emails):"]
    total = len(lines[0])
    
    for cat in [
        "business_info", "pricing", "policies", "faq",
        "email_templates", "contacts", "deadlines", "financials", "custom"
    ]:
        if cat not in grouped:
            continue
        label = CATEGORY_LABELS.get(cat, cat)
        section = f"\n[{label}]"
        for entry in grouped[cat]:
            item = f"\n- {entry.title}: {entry.content}"
            if total + len(section) + len(item) > max_chars:
                break
            section += item
        total += len(section)
        lines.append(section)
        if total > max_chars:
            break
    
    return "\n".join(lines)
