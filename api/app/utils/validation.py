"""
Input validation and sanitization utilities.
Protects against injection attacks and malformed data.
"""
import re
import html
from typing import Any, Optional, Dict, List
from pydantic import BaseModel, validator, Field
import bleach


# Allowed HTML tags for rich text content
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}


def sanitize_html(content: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    Only allows safe tags and attributes.
    """
    if not content:
        return ""
    
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """
    Sanitize plain text input.
    Escapes HTML and limits length.
    """
    if not text:
        return ""
    
    # Escape HTML entities
    text = html.escape(text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def sanitize_email(email: str) -> Optional[str]:
    """
    Validate and sanitize email address.
    Returns None if invalid.
    """
    if not email:
        return None
    
    email = email.strip().lower()
    
    # Basic email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return email
    
    return None


def sanitize_url(url: str, allowed_schemes: List[str] = None) -> Optional[str]:
    """
    Validate and sanitize URL.
    Returns None if invalid or uses disallowed scheme.
    """
    if not url:
        return None
    
    url = url.strip()
    allowed_schemes = allowed_schemes or ['http', 'https']
    
    # Parse URL
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        
        if parsed.scheme not in allowed_schemes:
            return None
        
        if not parsed.netloc:
            return None
        
        return url
    except Exception:
        return None


def sanitize_identifier(identifier: str, max_length: int = 100) -> str:
    """
    Sanitize an identifier (IDs, keys, names).
    Only allows alphanumeric, hyphens, and underscores.
    """
    if not identifier:
        return ""
    
    # Remove invalid characters
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', identifier)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def sanitize_phone(phone: str) -> Optional[str]:
    """
    Sanitize phone number.
    Returns E.164 format if valid, None otherwise.
    """
    if not phone:
        return None
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Ensure it starts with + for international format
    if not cleaned.startswith('+'):
        # Assume US number if 10 digits
        if len(cleaned) == 10:
            cleaned = '+1' + cleaned
        elif len(cleaned) == 11 and cleaned.startswith('1'):
            cleaned = '+' + cleaned
        else:
            return None
    
    # Validate length (E.164 is max 15 digits)
    if len(cleaned) < 10 or len(cleaned) > 16:
        return None
    
    return cleaned


def sanitize_json_data(data: Any, max_depth: int = 10, current_depth: int = 0) -> Any:
    """
    Recursively sanitize JSON data.
    Prevents deeply nested structures and sanitizes strings.
    """
    if current_depth > max_depth:
        return None
    
    if isinstance(data, str):
        return sanitize_text(data)
    elif isinstance(data, dict):
        return {
            sanitize_identifier(str(k)): sanitize_json_data(v, max_depth, current_depth + 1)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [sanitize_json_data(item, max_depth, current_depth + 1) for item in data[:1000]]
    elif isinstance(data, (int, float, bool, type(None))):
        return data
    else:
        return str(data)


class WorkflowConfigValidator(BaseModel):
    """Validator for workflow configuration data."""
    
    to: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    channel: Optional[str] = None
    message: Optional[str] = None
    spreadsheet: Optional[str] = None
    database_id: Optional[str] = None
    
    @validator('to')
    def validate_to(cls, v):
        if v and '{{' not in v:  # Skip template variables
            email = sanitize_email(v)
            if not email:
                # Could be a phone number
                phone = sanitize_phone(v)
                if not phone:
                    return sanitize_text(v, 200)
                return phone
            return email
        return sanitize_text(v, 200) if v else v
    
    @validator('subject', 'channel', 'spreadsheet', 'database_id')
    def validate_short_text(cls, v):
        return sanitize_text(v, 500) if v else v
    
    @validator('body', 'message')
    def validate_long_text(cls, v):
        return sanitize_text(v, 50000) if v else v


def validate_workflow_node(node: Dict) -> Dict:
    """
    Validate and sanitize a workflow node.
    """
    sanitized = {
        "id": sanitize_identifier(node.get("id", "")),
        "type": sanitize_identifier(node.get("type", "")),
        "label": sanitize_text(node.get("label", ""), 200),
        "position": node.get("position", {"x": 0, "y": 0}),
        "parameters": sanitize_json_data(node.get("parameters", {})),
        "requiresApproval": bool(node.get("requiresApproval", False)),
    }
    
    return sanitized


def validate_workflow_nodes(nodes: List[Dict]) -> List[Dict]:
    """Validate and sanitize all workflow nodes."""
    if not nodes:
        return []
    
    # Limit number of nodes
    if len(nodes) > 100:
        raise ValueError("Workflow cannot have more than 100 nodes")
    
    return [validate_workflow_node(node) for node in nodes]


def validate_webhook_payload(payload: Dict, max_size: int = 1_000_000) -> Dict:
    """
    Validate incoming webhook payload.
    
    Args:
        payload: The incoming JSON payload
        max_size: Maximum payload size in bytes
    
    Returns:
        Sanitized payload
    """
    import json
    
    # Check size
    payload_str = json.dumps(payload)
    if len(payload_str) > max_size:
        raise ValueError(f"Payload too large: {len(payload_str)} bytes (max: {max_size})")
    
    return sanitize_json_data(payload)
