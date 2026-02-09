"""
Email Service - SMTP-based email sending for when Google is not connected.
Also provides email templates.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from string import Template


class EmailService:
    """Service for sending emails via SMTP or external providers."""
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("FROM_EMAIL", self.smtp_user)
    
    @property
    def is_configured(self) -> bool:
        """Check if SMTP is configured."""
        return bool(self.smtp_user and self.smtp_password)
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> dict:
        """Send an email via SMTP."""
        if not self.is_configured:
            raise Exception("SMTP not configured. Set SMTP_USER and SMTP_PASSWORD.")
        
        # Create message
        if html_body:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
        else:
            msg = MIMEText(body)
        
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to
        
        if cc:
            msg["Cc"] = ", ".join(cc)
        
        # Collect all recipients
        recipients = [to]
        if cc:
            recipients.extend(cc)
        if bcc:
            recipients.extend(bcc)
        
        # Send email
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_email, recipients, msg.as_string())
        
        return {
            "success": True,
            "to": to,
            "subject": subject,
        }
    
    @staticmethod
    def render_template(
        template_name: str,
        variables: dict,
    ) -> tuple[str, str]:
        """Render an email template and return (subject, body)."""
        templates = {
            "welcome": {
                "subject": "Welcome to $company_name!",
                "body": """Hi $name,

Welcome to $company_name! We're excited to have you on board.

Here's what you can do next:
- Complete your profile
- Explore our features
- Reach out if you have any questions

Best regards,
The $company_name Team""",
                "html": """<h1>Welcome to $company_name!</h1>
<p>Hi $name,</p>
<p>Welcome to <strong>$company_name</strong>! We're excited to have you on board.</p>
<p>Here's what you can do next:</p>
<ul>
<li>Complete your profile</li>
<li>Explore our features</li>
<li>Reach out if you have any questions</li>
</ul>
<p>Best regards,<br>The $company_name Team</p>""",
            },
            "notification": {
                "subject": "Notification: $title",
                "body": """Hi $name,

$message

---
This is an automated notification from $company_name.""",
            },
            "follow_up": {
                "subject": "Following up: $subject",
                "body": """Hi $name,

I wanted to follow up on $subject.

$message

Let me know if you have any questions!

Best,
$sender_name""",
            },
            "invoice": {
                "subject": "Invoice #$invoice_number from $company_name",
                "body": """Hi $client_name,

Please find your invoice details below:

Invoice Number: $invoice_number
Amount: $amount
Due Date: $due_date

$payment_instructions

Thank you for your business!

Best regards,
$company_name""",
            },
            "appointment_reminder": {
                "subject": "Reminder: $appointment_type on $date",
                "body": """Hi $name,

This is a friendly reminder about your upcoming appointment:

Type: $appointment_type
Date: $date
Time: $time
Location: $location

$additional_notes

See you soon!

Best regards,
$company_name""",
            },
        }
        
        template = templates.get(template_name, {
            "subject": "$subject",
            "body": "$body",
        })
        
        subject = Template(template["subject"]).safe_substitute(variables)
        body = Template(template["body"]).safe_substitute(variables)
        html = Template(template.get("html", "")).safe_substitute(variables) if template.get("html") else None
        
        return subject, body, html


# Pre-defined email templates for workflow nodes
EMAIL_TEMPLATES = {
    "welcome_email": {
        "name": "Welcome Email",
        "subject": "Welcome to {{company}}!",
        "body": """Hi {{name}},

Welcome aboard! We're thrilled to have you join us.

{{custom_message}}

If you have any questions, just reply to this email.

Best,
{{sender_name}}""",
    },
    "follow_up_email": {
        "name": "Follow-up Email",
        "subject": "Following up on {{topic}}",
        "body": """Hi {{name}},

I wanted to follow up on {{topic}}.

{{custom_message}}

Looking forward to hearing from you!

Best,
{{sender_name}}""",
    },
    "thank_you_email": {
        "name": "Thank You Email",
        "subject": "Thank you, {{name}}!",
        "body": """Hi {{name}},

Thank you for {{reason}}!

{{custom_message}}

We appreciate your {{appreciation_type}}.

Best regards,
{{sender_name}}""",
    },
    "reminder_email": {
        "name": "Reminder Email",
        "subject": "Reminder: {{reminder_subject}}",
        "body": """Hi {{name}},

This is a friendly reminder about {{reminder_subject}}.

{{details}}

{{action_required}}

Best,
{{sender_name}}""",
    },
    "notification_email": {
        "name": "Notification Email",
        "subject": "{{notification_title}}",
        "body": """Hi {{name}},

{{notification_message}}

{{next_steps}}

Best,
{{sender_name}}""",
    },
}
