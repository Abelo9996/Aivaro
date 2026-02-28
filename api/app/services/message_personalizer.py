"""
Message Personalizer Service

Rewrites outbound messages (email, SMS, WhatsApp) to match the business's
communication style using their Knowledge Base context.
"""
import logging
from typing import Optional
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.services.knowledge_service import get_knowledge_context

logger = logging.getLogger(__name__)


async def personalize_message(
    draft: str,
    message_type: str,  # "email_body", "email_subject", "sms", "whatsapp", "slack"
    user_id: str,
    db: Session,
    recipient_context: str = "",  # e.g. "Customer: John Smith, booked auction item #42"
    additional_instructions: str = "",  # user-provided tone/style override
) -> str:
    """
    Rewrite a draft message to sound natural and match the business's voice.
    
    Returns the original draft if:
    - No OpenAI key configured
    - No knowledge base entries exist
    - The API call fails
    """
    if not settings.openai_api_key:
        return draft
    
    knowledge_ctx = get_knowledge_context(user_id, db, max_chars=3000)
    if not knowledge_ctx:
        # No knowledge base — can't personalize without business context
        return draft
    
    type_instructions = {
        "email_body": (
            "Rewrite this email body to sound natural and human — like the business owner wrote it themselves. "
            "Keep the same information and intent. Use appropriate greeting and sign-off. "
            "Don't be overly formal or robotic. Match the business's tone from the knowledge base."
        ),
        "email_subject": (
            "Rewrite this email subject line to sound natural and compelling. "
            "Keep it concise (under 60 chars). Don't use ALL CAPS or excessive punctuation."
        ),
        "sms": (
            "Rewrite this SMS to sound natural and friendly, like a real person texting. "
            "Keep it under 160 characters if possible. Be concise but warm. "
            "Don't start with 'Hi' if it makes the message too long."
        ),
        "whatsapp": (
            "Rewrite this WhatsApp message to sound natural and conversational. "
            "Can be slightly longer than SMS. Use a friendly, personal tone."
        ),
        "slack": (
            "Rewrite this Slack message to sound natural and professional but casual, "
            "matching typical Slack communication style."
        ),
    }
    
    instruction = type_instructions.get(message_type, type_instructions["email_body"])
    
    prompt = f"""{instruction}

{knowledge_ctx}

{f'RECIPIENT CONTEXT: {recipient_context}' if recipient_context else ''}
{f'ADDITIONAL STYLE INSTRUCTIONS: {additional_instructions}' if additional_instructions else ''}

DRAFT MESSAGE:
{draft}

REWRITTEN MESSAGE (output ONLY the rewritten message, no quotes, no explanation):"""

    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a message ghostwriter. You rewrite automated messages to sound like they were written by the business owner. Output ONLY the rewritten message."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        result = response.choices[0].message.content.strip()
        if result:
            logger.info(f"[Personalizer] Rewrote {message_type} ({len(draft)} -> {len(result)} chars)")
            return result
        return draft
    except Exception as e:
        logger.error(f"[Personalizer] Failed: {e}")
        return draft  # Graceful fallback — always send the original
