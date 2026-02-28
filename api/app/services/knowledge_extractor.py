"""Auto-extract knowledge from chat messages in the background."""
import logging
from sqlalchemy.orm import Session
from app.models import KnowledgeEntry

logger = logging.getLogger(__name__)

# Categories with extraction hints
EXTRACTION_PROMPT = """Analyze this user message from a business owner chatting with their AI assistant.
Extract ANY business knowledge that would be useful for future email replies, workflow creation, or task execution.

ONLY extract concrete, factual business information. Examples:
- "We charge $20 for deposits" → pricing: Deposit amount = $20
- "Our hours are 9-5 Mon-Fri" → business_info: Business hours = 9-5 Monday through Friday
- "We have a 24-hour cancellation policy" → policies: Cancellation policy = 24 hours notice required
- "My assistant Sarah handles bookings, sarah@company.com" → contacts: Sarah = bookings assistant, sarah@company.com
- "We need to file taxes by April 15" → deadlines: Tax filing deadline = April 15

DO NOT extract:
- Workflow instructions or automation requests
- Questions the user is asking
- Greetings or small talk
- Anything speculative or unclear

Respond with JSON array. Empty array [] if nothing to extract.
Each item: {"category": "...", "title": "short label", "content": "the actual info"}

Valid categories: business_info, pricing, policies, contacts, deadlines, financials, faq, email_templates, custom

User message: {message}

JSON:"""


def extract_knowledge_from_message(
    user_id: str,
    user_message: str,
    db: Session,
) -> list[dict]:
    """Extract and save knowledge entries from a user message. Returns list of saved entries."""
    from app.config import get_settings
    settings = get_settings()
    
    if not settings.openai_api_key:
        return []
    
    # Quick heuristic: skip short messages and obvious non-knowledge
    msg = user_message.strip()
    if len(msg) < 20:
        return []
    
    skip_patterns = [
        "show me", "list", "create a workflow", "build", "automate",
        "what", "how", "why", "can you", "help me", "tell me",
        "activate", "delete", "remove", "test", "run",
    ]
    msg_lower = msg.lower()
    if any(msg_lower.startswith(p) for p in skip_patterns):
        return []
    
    try:
        import openai
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        # Check plan limits before extracting
        from app.models import User as UserModel
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            limits = user.limits
            count = db.query(KnowledgeEntry).filter(KnowledgeEntry.user_id == user_id).count()
            if count >= limits.get("max_knowledge_entries", 3):
                logger.debug(f"[knowledge-extract] Skipping: user at knowledge limit ({count}/{limits.get('max_knowledge_entries')})")
                return []
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract structured business knowledge from chat messages. Respond ONLY with valid JSON arrays."},
                {"role": "user", "content": EXTRACTION_PROMPT.format(message=msg)},
            ],
            temperature=0,
            max_tokens=500,
        )
        
        import json
        raw = response.choices[0].message.content.strip()
        # Handle markdown code blocks
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        
        items = json.loads(raw)
        if not isinstance(items, list):
            return []
        
        saved = []
        valid_cats = {"business_info", "pricing", "policies", "contacts", "deadlines", "financials", "faq", "email_templates", "custom"}
        
        for item in items:
            cat = item.get("category", "")
            title = item.get("title", "").strip()
            content = item.get("content", "").strip()
            
            if not cat or cat not in valid_cats or not title or not content:
                continue
            
            # Check for duplicates (same title in same category)
            existing = db.query(KnowledgeEntry).filter(
                KnowledgeEntry.user_id == user_id,
                KnowledgeEntry.category == cat,
                KnowledgeEntry.title == title,
            ).first()
            
            if existing:
                # Update if content is different/longer
                if content != existing.content and len(content) >= len(existing.content):
                    existing.content = content
                    db.commit()
                    saved.append({"id": existing.id, "action": "updated", "title": title})
                continue
            
            entry = KnowledgeEntry(
                user_id=user_id,
                category=cat,
                title=title,
                content=content,
                priority=0,
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            saved.append({"id": entry.id, "action": "created", "title": title})
        
        if saved:
            logger.info(f"[knowledge-extract] Auto-extracted {len(saved)} entries: {[s['title'] for s in saved]}")
        
        return saved
        
    except Exception as e:
        logger.warning(f"[knowledge-extract] Extraction failed: {e}")
        return []
