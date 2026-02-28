"""
Email verification service - sends verification emails and validates tokens.
"""
import os
import secrets
import logging
from typing import Optional
from app.services.integrations.email_service import EmailService

logger = logging.getLogger(__name__)

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://www.aivaro-ai.com")
API_URL = os.getenv("API_URL", os.getenv("RAILWAY_PUBLIC_DOMAIN", ""))
if API_URL and not API_URL.startswith("http"):
    API_URL = f"https://{API_URL}"


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


def get_verification_link(token: str) -> str:
    """Build the verification URL that points to the frontend."""
    return f"{FRONTEND_URL}/verify?token={token}"


def send_verification_email(to_email: str, full_name: str, token: str) -> bool:
    """Send a verification email. Returns True if sent successfully."""
    email_service = EmailService()
    
    if not email_service.is_configured:
        logger.warning("[Email Verify] SMTP not configured, skipping verification email")
        return False
    
    link = get_verification_link(token)
    name = full_name or to_email.split("@")[0]
    
    subject = "Verify your Aivaro account"
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
  <div style="text-align: center; margin-bottom: 32px;">
    <h1 style="color: #6366f1; font-size: 28px; margin: 0;">Aivaro</h1>
    <p style="color: #666; margin-top: 4px;">AI Workflow Automation</p>
  </div>
  
  <div style="background: #f9fafb; border-radius: 12px; padding: 32px; margin-bottom: 24px;">
    <h2 style="margin-top: 0; font-size: 20px;">Welcome, {name}!</h2>
    <p style="line-height: 1.6;">Thanks for signing up for Aivaro. Please verify your email address to get started.</p>
    
    <div style="text-align: center; margin: 28px 0;">
      <a href="{link}" style="background: #6366f1; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block;">
        Verify Email Address
      </a>
    </div>
    
    <p style="font-size: 13px; color: #888; line-height: 1.5;">
      If the button doesn't work, copy and paste this link into your browser:<br>
      <a href="{link}" style="color: #6366f1; word-break: break-all;">{link}</a>
    </p>
  </div>
  
  <p style="font-size: 12px; color: #aaa; text-align: center;">
    If you didn't create an account on Aivaro, you can safely ignore this email.
  </p>
</body>
</html>"""
    
    text_body = f"""Welcome to Aivaro, {name}!

Please verify your email address by clicking this link:
{link}

If you didn't create an account on Aivaro, you can safely ignore this email."""
    
    try:
        email_service.send_email(
            to=to_email,
            subject=subject,
            body=text_body,
            html_body=html_body,
        )
        logger.info(f"[Email Verify] Verification email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"[Email Verify] Failed to send verification email to {to_email}: {e}")
        return False
