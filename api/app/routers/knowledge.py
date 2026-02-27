from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import logging

from app.database import get_db
from app.models import KnowledgeEntry, User
from app.schemas import KnowledgeCreate, KnowledgeUpdate, KnowledgeResponse, VALID_CATEGORIES
from app.routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


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
    from app.services.plan_limits import check_can_add_knowledge
    check_can_add_knowledge(current_user, db)

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


MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

SUPPORTED_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".pdf",
    ".doc", ".docx", ".rtf", ".html", ".htm",
}


def _extract_text_from_file(filename: str, content: bytes) -> str:
    """Extract readable text from uploaded file."""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext in (".txt", ".md", ".csv", ".html", ".htm", ".rtf"):
        # Try utf-8, fall back to latin-1
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")

    if ext == ".json":
        try:
            data = json.loads(content)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            return content.decode("utf-8", errors="replace")

    if ext == ".pdf":
        try:
            import io
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages).strip()
        except Exception:
            # PyPDF2 not installed or corrupt PDF
            try:
                # Fallback: extract raw text between stream markers
                text = content.decode("latin-1")
                return text
            except Exception:
                raise HTTPException(status_code=400, detail="Could not extract text from PDF. Install PyPDF2 for PDF support.")

    if ext in (".doc", ".docx"):
        try:
            import io
            import docx
            doc = docx.Document(io.BytesIO(content))
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception:
            raise HTTPException(status_code=400, detail="Could not extract text from document. Install python-docx for .docx support.")

    raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")


async def _ai_extract_knowledge(text: str) -> list[dict]:
    """Use OpenAI to extract meaningful knowledge entries from file text."""
    import os
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Fallback: return as a single entry
        return [{"category": "custom", "title": "Imported Document", "content": text[:4000], "priority": 0}]

    client = openai.AsyncOpenAI(api_key=api_key)

    # Truncate very long docs
    truncated = text[:12000]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You extract business knowledge from documents. Return a JSON array of knowledge entries.

Each entry must have:
- "category": one of: business_info, pricing, policies, contacts, deadlines, financials, faq, email_templates, custom
- "title": short descriptive title (3-8 words)
- "content": the actual knowledge (be specific, keep details, 1-3 sentences each)
- "priority": 0 (normal), 1 (high), or 2 (critical)

Rules:
- Extract ALL meaningful business information — pricing, policies, contacts, hours, services, etc.
- Each piece of information should be its own entry (don't lump everything together)
- Skip boilerplate, headers, formatting artifacts
- Keep the original specifics (numbers, names, dates, amounts)
- If nothing meaningful can be extracted, return an empty array []

Return ONLY valid JSON array, no markdown.""",
                },
                {"role": "user", "content": f"Extract knowledge entries from this document:\n\n{truncated}"},
            ],
            temperature=0.1,
            max_tokens=4000,
        )

        result_text = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1] if "\n" in result_text else result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

        entries = json.loads(result_text)
        if not isinstance(entries, list):
            entries = [entries]

        # Validate
        valid = []
        for e in entries:
            if isinstance(e, dict) and e.get("title") and e.get("content"):
                cat = e.get("category", "custom")
                if cat not in VALID_CATEGORIES:
                    cat = "custom"
                valid.append({
                    "category": cat,
                    "title": str(e["title"])[:200],
                    "content": str(e["content"])[:2000],
                    "priority": min(max(int(e.get("priority", 0)), 0), 2),
                })
        return valid if valid else [{"category": "custom", "title": "Imported Document", "content": truncated[:4000], "priority": 0}]

    except Exception as exc:
        logger.warning(f"[knowledge-import] AI extraction failed: {exc}")
        return [{"category": "custom", "title": "Imported Document", "content": truncated[:4000], "priority": 0}]


@router.post("/import", response_model=List[KnowledgeResponse])
async def import_knowledge_from_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a file and extract knowledge entries from it using AI."""
    from app.services.plan_limits import check_can_import_file
    check_can_import_file(current_user)
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 2MB)")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    # Extract text
    text = _extract_text_from_file(file.filename, content)
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract any text from file")

    # AI extraction
    extracted = await _ai_extract_knowledge(text.strip())

    # Save entries
    created = []
    for entry_data in extracted:
        entry = KnowledgeEntry(
            user_id=current_user.id,
            category=entry_data["category"],
            title=entry_data["title"],
            content=entry_data["content"],
            priority=entry_data.get("priority", 0),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        created.append(KnowledgeResponse.model_validate(entry))

    return created
