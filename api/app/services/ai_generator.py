import json
from typing import Optional, List, Dict, Any

from app.config import get_settings

settings = get_settings()


# ============================================================
# WORKFLOW CLARIFICATION SYSTEM
# Asks clarifying questions before generating a workflow
# ============================================================

CLARIFICATION_CATEGORIES = {
    "trigger": {
        "question": "What should trigger this workflow?",
        "options": [
            "When I manually start it",
            "When someone fills out a form",
            "On a schedule (daily, weekly, etc.)",
            "When I receive an email",
            "When a webhook is received"
        ]
    },
    "frequency": {
        "question": "How often should this run?",
        "applies_to": ["schedule"],
    },
    "data_source": {
        "question": "Where is the data coming from?",
        "options": [
            "A form submission",
            "An email",
            "A Google Sheet",
            "An Airtable base",
            "A Notion database",
            "An API/webhook"
        ]
    },
    "actions": {
        "question": "What actions should happen? (Select all that apply)",
        "options": [
            "Send an email",
            "Add to a spreadsheet",
            "Create a calendar event",
            "Send a Slack message",
            "Send an SMS",
            "Create a payment/invoice",
            "Update a database record",
            "Generate AI content"
        ]
    },
    "approval": {
        "question": "Should any steps require your approval before running?",
        "options": [
            "Yes, I want to review emails before they're sent",
            "Yes, I want to review payments before they're created",
            "No, run everything automatically"
        ]
    }
}


def analyze_prompt_completeness(prompt: str) -> Dict[str, Any]:
    """
    Analyze a prompt to determine what clarifying questions are needed.
    Returns a dict with:
    - is_complete: Whether the prompt has enough detail to generate
    - missing_info: List of what's unclear
    - questions: List of clarifying questions to ask
    - confidence: 0-100 score of how confident we are
    """
    if settings.openai_api_key:
        return _analyze_with_openai(prompt)
    return _analyze_deterministic(prompt)


def _analyze_with_openai(prompt: str) -> Dict[str, Any]:
    """Use OpenAI to analyze prompt completeness"""
    try:
        import openai
        
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        analysis_prompt = """You are a workflow automation expert. Analyze the user's request and determine if it has enough detail to build a reliable workflow.

A COMPLETE request should clearly specify:
1. TRIGGER: What starts the workflow (form, email, schedule, manual, webhook)
2. DATA: What data is involved and where it comes from
3. ACTIONS: What specific actions should happen
4. RECIPIENTS: Who receives emails/notifications (if applicable)
5. TIMING: Any delays, schedules, or conditional timing
6. INTEGRATIONS: Which tools are needed (Gmail, Sheets, Slack, etc.)

Analyze the request and return a JSON object:
{
  "is_complete": boolean (true only if ALL necessary details are clear),
  "confidence": number 0-100 (how confident you are about what to build),
  "understood": {
    "trigger": "what you understood about the trigger, or null",
    "data_source": "what you understood about data, or null",
    "actions": ["list of actions you understood"],
    "recipients": "who receives output, or null",
    "integrations": ["list of tools needed"]
  },
  "missing_info": ["list of unclear or missing details"],
  "questions": [
    {
      "id": "unique_id",
      "question": "The clarifying question to ask",
      "why": "Brief reason why this matters",
      "options": ["option1", "option2", "option3"] or null for free-text,
      "allow_multiple": boolean (true if multiple options can be selected)
    }
  ]
}

IMPORTANT RULES:
- If confidence < 70, you MUST ask clarifying questions
- Ask 2-4 focused questions maximum
- Questions should be specific, not generic
- Options should cover common use cases
- Always ask about approval requirements for email/payment workflows
- For vague requests like "automate my business", ask what specific task they want to start with

Return ONLY valid JSON."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": f"Analyze this workflow request: {prompt}"}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        # Strip markdown if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        result = json.loads(content.strip())
        
        # Ensure required fields exist
        result.setdefault("is_complete", False)
        result.setdefault("confidence", 50)
        result.setdefault("questions", [])
        result.setdefault("missing_info", [])
        result.setdefault("understood", {})
        
        return result
        
    except Exception as e:
        print(f"OpenAI analysis failed: {e}")
        return _analyze_deterministic(prompt)


def _analyze_deterministic(prompt: str) -> Dict[str, Any]:
    """Analyze prompt using keyword matching"""
    prompt_lower = prompt.lower()
    
    understood = {
        "trigger": None,
        "data_source": None,
        "actions": [],
        "recipients": None,
        "integrations": []
    }
    missing = []
    questions = []
    confidence = 30  # Start low
    
    # Check for trigger
    trigger_keywords = {
        "form": ("form", "submitted", "submission", "fills out"),
        "email": ("email", "receive", "inbox", "gmail"),
        "schedule": ("daily", "weekly", "every day", "every week", "schedule", "morning", "evening"),
        "manual": ("manually", "when i click", "on demand"),
        "webhook": ("webhook", "api call", "external")
    }
    
    for trigger_type, keywords in trigger_keywords.items():
        if any(kw in prompt_lower for kw in keywords):
            understood["trigger"] = trigger_type
            confidence += 15
            break
    
    if not understood["trigger"]:
        missing.append("What triggers this workflow")
        questions.append({
            "id": "trigger",
            "question": "What should start this workflow?",
            "why": "I need to know what event kicks off the automation",
            "options": [
                "When someone submits a form",
                "When I receive an email",
                "On a schedule (daily, weekly, etc.)",
                "When I manually click 'Run'",
                "When an external system sends data (webhook)"
            ],
            "allow_multiple": False
        })
    
    # Check for actions
    action_keywords = {
        "send_email": ("send email", "email them", "reply", "respond"),
        "spreadsheet": ("spreadsheet", "google sheet", "log", "record"),
        "calendar": ("calendar", "schedule", "appointment", "booking", "event"),
        "slack": ("slack", "message team"),
        "sms": ("sms", "text message", "twilio"),
        "payment": ("payment", "invoice", "stripe", "charge", "deposit"),
        "ai": ("ai", "generate", "summarize", "draft")
    }
    
    for action_type, keywords in action_keywords.items():
        if any(kw in prompt_lower for kw in keywords):
            understood["actions"].append(action_type)
            confidence += 10
    
    if not understood["actions"]:
        missing.append("What actions should happen")
        questions.append({
            "id": "actions",
            "question": "What should happen when this workflow runs?",
            "why": "I need to know what actions to perform",
            "options": [
                "Send an email",
                "Add data to a spreadsheet",
                "Create a calendar event",
                "Send a Slack message",
                "Create a payment link or invoice",
                "Generate AI content"
            ],
            "allow_multiple": True
        })
    
    # Check if email is involved but no recipient clarity
    if "email" in understood["actions"] or "send_email" in str(understood["actions"]):
        if not any(word in prompt_lower for word in ["to the", "back to", "reply", "{{", "customer", "client", "user"]):
            missing.append("Who should receive the email")
            questions.append({
                "id": "email_recipient",
                "question": "Who should receive the email?",
                "why": "I need to know the recipient",
                "options": [
                    "Reply to the person who triggered it (e.g., form submitter, email sender)",
                    "Send to a specific email address",
                    "Send to my team/internal"
                ],
                "allow_multiple": False
            })
    
    # Check for payment/booking but no amount
    if any(word in prompt_lower for word in ["payment", "deposit", "charge", "invoice"]):
        if not any(char.isdigit() for char in prompt):
            questions.append({
                "id": "payment_amount",
                "question": "What should the payment amount be?",
                "why": "I need to set the correct price",
                "options": None,  # Free text
                "allow_multiple": False
            })
            confidence -= 10
    
    # Always ask about approval for sensitive actions
    sensitive_actions = ["send_email", "payment", "sms"]
    if any(action in str(understood["actions"]) for action in sensitive_actions):
        questions.append({
            "id": "approval",
            "question": "Should you review and approve before these actions run?",
            "why": "This adds a safety check before sending emails or processing payments",
            "options": [
                "Yes, I want to review before sending",
                "No, run automatically"
            ],
            "allow_multiple": False
        })
    
    # Determine if complete
    is_complete = confidence >= 70 and len(questions) <= 1
    
    return {
        "is_complete": is_complete,
        "confidence": min(confidence, 100),
        "understood": understood,
        "missing_info": missing,
        "questions": questions[:4]  # Max 4 questions
    }


def generate_workflow_with_context(prompt: str, clarifications: Dict[str, Any] = None) -> dict:
    """
    Generate a workflow with additional context from clarifying questions.
    
    Args:
        prompt: Original user prompt
        clarifications: Dict of question_id -> answer from clarifying questions
    """
    # Build enhanced prompt with clarifications
    enhanced_prompt = prompt
    
    if clarifications:
        enhanced_prompt += "\n\nAdditional details:"
        for question_id, answer in clarifications.items():
            if isinstance(answer, list):
                answer = ", ".join(answer)
            enhanced_prompt += f"\n- {question_id}: {answer}"
    
    return generate_workflow_from_prompt(enhanced_prompt)


def generate_workflow_from_prompt(prompt: str) -> dict:
    """Generate a workflow from a plain English prompt"""
    
    # If OpenAI key is available, use it
    if settings.openai_api_key:
        return _generate_with_openai(prompt)
    
    # Otherwise, use deterministic generator
    return _generate_deterministic(prompt)


def _generate_with_openai(prompt: str) -> dict:
    """Use OpenAI to generate workflow"""
    try:
        import openai
        
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        system_prompt = """You are a workflow automation assistant for Aivaro, a tool that helps non-technical founders automate their business processes.

Generate a workflow based on the user's description. Return a JSON object with:
- workflowName: A short, descriptive name (3-5 words)
- summary: A plain English sentence starting with "When... Aivaro will..."
- nodes: Array of nodes with {id, type, label, position: {x, y}, parameters, requiresApproval}
- edges: Array of edges with {id, source, target}

Available TRIGGER node types (must be first node):
- start_manual: Manual start trigger (when user clicks "Run")
- start_form: Form submission trigger (when someone fills a form)
- start_schedule: Scheduled trigger (runs on a schedule). Parameters: {time: "09:00", frequency: "daily/weekly/monthly"}
- start_email: Email received trigger - monitors the user's CONNECTED Gmail account for new emails matching criteria. Use this when user says "when I receive an email", "when an email comes in", "when I get an email", etc. Parameters: {subject: "keyword to match", from: "optional@sender.com"}

IMPORTANT: When the user mentions receiving emails, getting emails, or email triggers, they mean their connected Gmail account. The start_email trigger monitors their Gmail inbox automatically.

Available ACTION node types:
- send_email: Send an email. Parameters: {to: "{{from}}", subject: "Re: {{subject}}", body: "..."}
- ai_reply: Generate an AI response to an email. IMPORTANT: This only GENERATES a reply — it does NOT send it. You MUST add a send_email step after ai_reply to actually deliver the response. Parameters: {context: "...", tone: "professional/friendly/casual"}. Output: {{ai_response}}
- ai_summarize: Use AI to summarize data. Parameters: {source: "...", format: "bullet_points/paragraph"}
- append_row: Add row to Google Sheets. Parameters: {spreadsheet: "...", sheet_name: "Sheet1", columns: [{name: "...", value: "{{...}}"}]}
- read_sheet: Read data from Google Sheets. Parameters: {spreadsheet_id: "...", range: "A1:D10"}
- delay: Wait for a duration. Parameters: {duration: 2, unit: "hours/minutes/days"}
- send_notification: Send a notification. Parameters: {message: "..."}
- send_slack: Send a Slack message. Parameters: {channel: "#general", message: "..."}
- http_request: Make an API call. Parameters: {url: "...", method: "GET/POST"}
- condition: Branch based on conditions. Parameters: {condition: "if {{status}} == 'approved'"}

GOOGLE CALENDAR node types:
- google_calendar_create: Create a calendar event. Parameters: {title: "Meeting with {{name}}", date: "{{date}}", start_time: "{{time}}", duration: 1, description: "...", location: "..."}

STRIPE PAYMENT node types (use these for deposits, payments, invoices):
- stripe_create_payment_link: Create a payment/deposit link. Parameters: {amount: 20, product_name: "Deposit", success_message: "Thank you!"}
- stripe_check_payment: Check if payment was made. Parameters: {payment_link_id: "{{payment_link_id}}", customer_email: "{{email}}"}
- stripe_create_invoice: Create an invoice. Parameters: {customer_email: "{{email}}", amount: 100, description: "Service", due_days: 30, auto_send: "true"}
- stripe_send_invoice: Send an existing invoice. Parameters: {invoice_id: "{{invoice_id}}"}
- stripe_get_customer: Get or create a Stripe customer. Parameters: {email: "{{email}}", name: "{{name}}"}

NOTION node types (for notes, databases, documentation):
- notion_create_page: Create a page in a Notion database. Parameters: {database_id: "...", properties: {Title: "{{name}}", Status: "New"}, content: "..."}
- notion_update_page: Update a Notion page. Parameters: {page_id: "{{notion_page_id}}", properties: {Status: "Completed"}}
- notion_query_database: Query records from a Notion database. Parameters: {database_id: "...", page_size: 100}
- notion_search: Search across Notion. Parameters: {query: "{{search_term}}", filter_type: "page/database"}

AIRTABLE node types (for database operations, CRM):
- airtable_create_record: Create a record in Airtable. Parameters: {base_id: "appXXX", table_name: "Customers", fields: {Name: "{{name}}", Email: "{{email}}"}}
- airtable_update_record: Update an Airtable record. Parameters: {base_id: "appXXX", table_name: "Customers", record_id: "{{airtable_record_id}}", fields: {Status: "Active"}}
- airtable_list_records: List records from Airtable. Parameters: {base_id: "appXXX", table_name: "Customers", max_records: 100}
- airtable_find_record: Find a record by field value. Parameters: {base_id: "appXXX", table_name: "Customers", field_name: "Email", field_value: "{{email}}"}

CALENDLY node types (for scheduling):
- calendly_list_events: List scheduled Calendly events. Parameters: {status: "active", count: 20}
- calendly_get_event: Get details of a Calendly event. Parameters: {event_uuid: "{{calendly_event_uuid}}"}
- calendly_cancel_event: Cancel a Calendly event. Parameters: {event_uuid: "{{calendly_event_uuid}}", reason: "..."}
- calendly_create_link: Create a single-use scheduling link. Parameters: {event_type_uuid: "...", max_event_count: 1}

MAILCHIMP node types (for email marketing):
- mailchimp_add_subscriber: Add/update subscriber to an audience. Parameters: {list_id: "...", email: "{{email}}", first_name: "{{first_name}}", last_name: "{{last_name}}", status: "subscribed", tags: ["customer"]}
- mailchimp_add_tags: Add tags to a subscriber. Parameters: {list_id: "...", email: "{{email}}", tags: ["vip", "customer"]}
- mailchimp_send_campaign: Create and send a campaign. Parameters: {list_id: "...", subject: "...", from_name: "...", reply_to: "...", html_content: "..."}

TWILIO node types (for SMS and calls):
- twilio_send_sms: Send an SMS message. Parameters: {to: "{{phone}}", body: "Hi {{name}}, your booking is confirmed!"}
- twilio_send_whatsapp: Send a WhatsApp message. Parameters: {to: "{{phone}}", body: "...", media_url: "..."}
- twilio_make_call: Make a phone call with a message. Parameters: {to: "{{phone}}", message: "Hello, this is a reminder about..."}

IMPORTANT RULES:
1. For booking/appointment workflows with deposits → use google_calendar_create + stripe_create_payment_link
2. For payment reminders → use delay + stripe_check_payment + condition
3. When user says "when I receive an email", "when I get an email", "when an email comes in", "emails from X", etc. → ALWAYS use start_email trigger. This monitors their connected Gmail inbox.
4. For auto-reply workflows → use ai_reply node to generate smart responses, then ALWAYS follow with a send_email node to actually send the reply. ai_reply generates the text, send_email delivers it. Never create an email reply workflow without a send_email step.
5. COMPLETE EMAIL REPLY PATTERN: start_email → ai_reply → send_email (to={{from}}, subject="Re: {{subject}}", body="{{ai_response}}").
6. For Stripe invoices with auto_send=false → MUST add a stripe_send_invoice step after stripe_create_invoice.
7. For Stripe invoices with auto_send=true → no additional send step needed, but tell the user the invoice will be auto-sent.
8. mailchimp_send_campaign creates AND immediately sends — this is irreversible. ALWAYS set requiresApproval=true on this node.
9. twilio_make_call uses text-to-speech (robotic voice). Note this in the step label or description.
10. PLACEHOLDER VALUES: When using Airtable (base_id: "appXXX"), Notion (database_id), Calendly (event_type_uuid), or Mailchimp (list_id) — these are placeholders. The user MUST fill them in from their actual account. Flag these clearly.
11. For CRM/database workflows → prefer airtable_create_record or notion_create_page for storing customer data
12. For marketing/newsletter workflows → use mailchimp_add_subscriber to add contacts
13. For SMS notifications → use twilio_send_sms for text confirmations
14. For scheduling links → use calendly_create_link to generate booking links
15. Available template variables: {{from}}, {{to}}, {{subject}}, {{snippet}}, {{email}}, {{name}}, {{date}}, {{time}}, {{amount}}, {{payment_link_url}}, {{phone}}, {{ai_response}}
16. Always connect nodes with edges
17. Position nodes vertically, starting at y=50, spaced 150px apart, x=250
18. Set requiresApproval: true for: emails to external recipients, payment processing, campaign sends, phone calls. Set to false for: internal notifications, logging to sheets, calendar events.
19. The start_email trigger monitors the user's connected Gmail account - do NOT ask them to set up webhooks or external services
20. NEVER use node types not listed above. Only use the exact types defined here.

Example for "booking automation with deposit":
{
  "workflowName": "Booking with Deposit",
  "summary": "When a booking form is submitted, Aivaro will create a calendar event, generate a deposit link, and send a confirmation email.",
  "nodes": [
    {"id": "1", "type": "start_form", "label": "When booking form submitted", "position": {"x": 250, "y": 50}, "parameters": {}, "requiresApproval": false},
    {"id": "2", "type": "google_calendar_create", "label": "Create pickup event", "position": {"x": 250, "y": 200}, "parameters": {"title": "Pickup — {{name}}", "date": "{{pickup_date}}", "start_time": "{{pickup_time}}", "duration": 1, "description": "Customer: {{name}}\\nPhone: {{phone}}"}, "requiresApproval": false},
    {"id": "3", "type": "stripe_create_payment_link", "label": "Create $20 deposit link", "position": {"x": 250, "y": 350}, "parameters": {"amount": 20, "product_name": "Booking Deposit", "success_message": "Your booking is confirmed!"}, "requiresApproval": false},
    {"id": "4", "type": "send_email", "label": "Send confirmation with payment link", "position": {"x": 250, "y": 500}, "parameters": {"to": "{{email}}", "subject": "Confirm your booking - deposit required", "body": "Hi {{name}},\\n\\nYour pickup is scheduled for {{pickup_date}} at {{pickup_time}}.\\n\\nPlease pay the $20 deposit to confirm: {{payment_link_url}}\\n\\nThank you!"}, "requiresApproval": false},
    {"id": "5", "type": "append_row", "label": "Log to spreadsheet", "position": {"x": 250, "y": 650}, "parameters": {"spreadsheet": "Bookings", "columns": [{"name": "Name", "value": "{{name}}"}, {"name": "Date", "value": "{{pickup_date}}"}, {"name": "Status", "value": "Pending Deposit"}]}, "requiresApproval": false}
  ],
  "edges": [{"id": "e1", "source": "1", "target": "2"}, {"id": "e2", "source": "2", "target": "3"}, {"id": "e3", "source": "3", "target": "4"}, {"id": "e4", "source": "4", "target": "5"}]
}

Return ONLY valid JSON, no markdown code blocks or explanation."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a workflow for: {prompt}"}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content
        # Strip markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())
        
    except Exception as e:
        print(f"OpenAI generation failed: {e}")
        return _generate_deterministic(prompt)


def _generate_deterministic(prompt: str) -> dict:
    """Generate workflow using keyword matching"""
    prompt_lower = prompt.lower()
    
    # First, check for email-triggered workflows (higher priority)
    # These phrases indicate the user wants to trigger on emails from their connected Gmail
    is_email_trigger = any(phrase in prompt_lower for phrase in [
        "when i receive", "when i get", "when an email", "when email",
        "receive an email", "get an email", "email comes in", "email arrives",
        "incoming email", "new email", "subject", "inbox", 
        "appointment scheduled", "booking confirmation", "when someone emails",
        "emails from", "email from", "receive a", "when a customer emails"
    ])
    
    # Detect workflow type based on keywords
    if any(word in prompt_lower for word in ["booking", "appointment", "schedule", "pickup"]):
        return _template_booking_workflow(email_trigger=is_email_trigger, prompt=prompt)
    elif any(word in prompt_lower for word in ["lead", "follow up", "prospect"]):
        return _template_lead_followup()
    elif any(word in prompt_lower for word in ["order", "purchase", "receipt"]):
        return _template_order_workflow()
    elif any(word in prompt_lower for word in ["invoice", "payment", "overdue"]):
        return _template_invoice_workflow()
    elif any(word in prompt_lower for word in ["report", "summary", "daily", "weekly"]):
        return _template_report_workflow()
    elif is_email_trigger:
        # Generic email workflow
        return _template_email_workflow(prompt)
    else:
        return _template_generic_workflow(prompt)


def _template_booking_workflow(email_trigger: bool = False, prompt: str = "") -> dict:
    # Extract subject filter from prompt if mentioned
    subject_filter = ""
    prompt_lower = prompt.lower()
    if "appointment scheduled" in prompt_lower:
        subject_filter = "Appointment Scheduled"
    elif "booking" in prompt_lower and "subject" in prompt_lower:
        subject_filter = "Booking"
    
    # Choose trigger type based on detection
    if email_trigger:
        # Email-triggered workflow needs AI to extract booking details
        return {
            "workflowName": "Booking with Deposit",
            "summary": f"When an email arrives with \"{subject_filter or 'Appointment Scheduled'}\" in the subject, Aivaro will extract booking details, create a calendar event, generate a deposit payment link, send confirmation, and log it to your spreadsheet.",
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_email",
                    "label": f"Email with \"{subject_filter or 'Appointment Scheduled'}\"",
                    "position": {"x": 250, "y": 50},
                    "parameters": {
                        "subject": subject_filter or "Appointment Scheduled"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "extract-1",
                    "type": "ai_extract",
                    "label": "Extract booking details from email",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "fields": "customer_name, customer_email, pickup_date, pickup_time, phone, service",
                        "context": "Extract the customer name, their email, the scheduled pickup date (YYYY-MM-DD format), time (HH:MM format), phone number, and service type from this booking confirmation email."
                    },
                    "requiresApproval": False
                },
                {
                    "id": "calendar-1",
                    "type": "google_calendar_create",
                    "label": "Create pickup event",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "title": "Pickup — {{customer_name}}",
                        "date": "{{pickup_date}}",
                        "start_time": "{{pickup_time}}",
                        "duration": 1,
                        "description": "Customer: {{customer_name}}\nPhone: {{phone}}\nService: {{service}}\nEmail: {{customer_email}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "stripe-1",
                    "type": "stripe_create_payment_link",
                    "label": "Create $20 deposit link",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "amount": 20,
                        "product_name": "Booking Deposit - {{service}}",
                        "success_message": "Your booking is confirmed! We'll see you on {{pickup_date}}."
                    },
                    "requiresApproval": True
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send confirmation with payment link",
                    "position": {"x": 250, "y": 650},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Confirm your booking - $20 deposit required",
                        "body": "Hi {{customer_name}},\n\nYour {{service}} pickup is scheduled for {{pickup_date}} at {{pickup_time}}.\n\nTo confirm your booking, please pay the $20 deposit:\n{{payment_link_url}}\n\nOnce paid, your booking is locked in!\n\nThank you!"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log to bookings spreadsheet",
                    "position": {"x": 250, "y": 800},
                    "parameters": {
                        "spreadsheet": "Bookings Log",
                        "columns": [
                            {"name": "Date", "value": "{{pickup_date}}"},
                            {"name": "Time", "value": "{{pickup_time}}"},
                            {"name": "Name", "value": "{{customer_name}}"},
                            {"name": "Email", "value": "{{customer_email}}"},
                            {"name": "Phone", "value": "{{phone}}"},
                            {"name": "Service", "value": "{{service}}"},
                            {"name": "Deposit Status", "value": "Pending"},
                            {"name": "Payment Link", "value": "{{payment_link_url}}"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Notify you of new booking",
                    "position": {"x": 250, "y": 950},
                    "parameters": {
                        "message": "New booking: {{customer_name}} for {{service}} on {{pickup_date}} - Deposit link sent"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "extract-1"},
                {"id": "e2", "source": "extract-1", "target": "calendar-1"},
                {"id": "e3", "source": "calendar-1", "target": "stripe-1"},
                {"id": "e4", "source": "stripe-1", "target": "email-1"},
                {"id": "e5", "source": "email-1", "target": "sheet-1"},
                {"id": "e6", "source": "sheet-1", "target": "notify-1"}
            ]
        }
    else:
        # Form-triggered workflow - data comes from form fields
        return {
            "workflowName": "Booking with Deposit",
            "summary": "When a new booking form is submitted, Aivaro will create a calendar event, generate a deposit payment link, send confirmation, and log it to your spreadsheet.",
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When booking form is submitted",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "calendar-1",
                    "type": "google_calendar_create",
                    "label": "Create pickup event",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "title": "Pickup — {{name}}",
                        "date": "{{pickup_date}}",
                        "start_time": "{{pickup_time}}",
                        "duration": 1,
                        "description": "Customer: {{name}}\nPhone: {{phone}}\nService: {{service}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "stripe-1",
                    "type": "stripe_create_payment_link",
                    "label": "Create $20 deposit link",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "amount": 20,
                        "product_name": "Booking Deposit - {{service}}",
                        "success_message": "Your booking is confirmed! We'll see you on {{pickup_date}}."
                    },
                    "requiresApproval": True
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send confirmation with payment link",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Confirm your booking - $20 deposit required",
                        "body": "Hi {{name}},\n\nYour {{service}} pickup is scheduled for {{pickup_date}} at {{pickup_time}}.\n\nTo confirm your booking, please pay the $20 deposit:\n{{payment_link_url}}\n\nOnce paid, your booking is locked in!\n\nThank you!"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log to bookings spreadsheet",
                    "position": {"x": 250, "y": 650},
                    "parameters": {
                        "spreadsheet": "Bookings Log",
                        "columns": [
                            {"name": "Date", "value": "{{pickup_date}}"},
                            {"name": "Time", "value": "{{pickup_time}}"},
                            {"name": "Name", "value": "{{name}}"},
                            {"name": "Email", "value": "{{email}}"},
                            {"name": "Service", "value": "{{service}}"},
                            {"name": "Deposit Status", "value": "Pending"},
                            {"name": "Payment Link", "value": "{{payment_link_url}}"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Notify you of new booking",
                    "position": {"x": 250, "y": 800},
                    "parameters": {
                        "message": "New booking: {{name}} for {{service}} on {{pickup_date}} - Deposit link sent"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "calendar-1"},
                {"id": "e2", "source": "calendar-1", "target": "stripe-1"},
                {"id": "e3", "source": "stripe-1", "target": "email-1"},
                {"id": "e4", "source": "email-1", "target": "sheet-1"},
                {"id": "e5", "source": "sheet-1", "target": "notify-1"}
            ]
        }


def _template_email_workflow(prompt: str = "") -> dict:
    """Generic email-triggered workflow"""
    return {
        "workflowName": "Email Auto-Response",
        "summary": "When an email arrives, Aivaro will generate an AI response and reply.",
        "nodes": [
            {
                "id": "start-1",
                "type": "start_email",
                "label": "When email is received",
                "position": {"x": 250, "y": 50},
                "parameters": {},
                "requiresApproval": False
            },
            {
                "id": "ai-1",
                "type": "ai_reply",
                "label": "Generate AI response",
                "position": {"x": 250, "y": 200},
                "parameters": {
                    "tone": "professional",
                    "context": "Reply helpfully to this email"
                },
                "requiresApproval": False
            },
            {
                "id": "email-1",
                "type": "send_email",
                "label": "Send reply",
                "position": {"x": 250, "y": 350},
                "parameters": {
                    "to": "{{from}}",
                    "subject": "Re: {{subject}}",
                    "body": "{{ai_response}}"
                },
                "requiresApproval": True
            }
        ],
        "edges": [
            {"id": "e1", "source": "start-1", "target": "ai-1"},
            {"id": "e2", "source": "ai-1", "target": "email-1"}
        ]
    }


def _template_lead_followup() -> dict:
    return {
        "workflowName": "Lead Follow-up Sequence",
        "summary": "When a new lead comes in, Aivaro will send follow-up emails until they respond or book.",
        "nodes": [
            {
                "id": "start-1",
                "type": "start_form",
                "label": "When lead form is submitted",
                "position": {"x": 250, "y": 50},
                "parameters": {},
                "requiresApproval": False
            },
            {
                "id": "email-1",
                "type": "send_email",
                "label": "Send initial response",
                "position": {"x": 250, "y": 200},
                "parameters": {
                    "to": "{{email}}",
                    "subject": "Thanks for reaching out!",
                    "body": "Hi {{name}},\n\nThanks for your interest! I'd love to learn more about how I can help you.\n\nWould you be available for a quick call this week?"
                },
                "requiresApproval": True
            },
            {
                "id": "delay-1",
                "type": "delay",
                "label": "Wait 2 days",
                "position": {"x": 250, "y": 350},
                "parameters": {
                    "duration": 2,
                    "unit": "days"
                },
                "requiresApproval": False
            },
            {
                "id": "email-2",
                "type": "send_email",
                "label": "Send follow-up email",
                "position": {"x": 250, "y": 500},
                "parameters": {
                    "to": "{{email}}",
                    "subject": "Quick follow-up",
                    "body": "Hi {{name}},\n\nJust wanted to follow up on my previous email. Do you have a few minutes to chat?\n\nHere's my calendar link to book a time that works for you."
                },
                "requiresApproval": True
            }
        ],
        "edges": [
            {"id": "e1", "source": "start-1", "target": "email-1"},
            {"id": "e2", "source": "email-1", "target": "delay-1"},
            {"id": "e3", "source": "delay-1", "target": "email-2"}
        ]
    }


def _template_order_workflow() -> dict:
    return {
        "workflowName": "New Order Processing",
        "summary": "When a new order comes in, Aivaro will send a receipt and log it to your orders spreadsheet.",
        "nodes": [
            {
                "id": "start-1",
                "type": "start_form",
                "label": "When order is placed",
                "position": {"x": 250, "y": 50},
                "parameters": {},
                "requiresApproval": False
            },
            {
                "id": "email-1",
                "type": "send_email",
                "label": "Send order receipt",
                "position": {"x": 250, "y": 200},
                "parameters": {
                    "to": "{{email}}",
                    "subject": "Order Confirmation #{{order_id}}",
                    "body": "Hi {{name}},\n\nThank you for your order!\n\nOrder total: ${{amount}}\n\nWe'll notify you when it ships."
                },
                "requiresApproval": True
            },
            {
                "id": "sheet-1",
                "type": "append_row",
                "label": "Log to orders spreadsheet",
                "position": {"x": 250, "y": 350},
                "parameters": {
                    "spreadsheet": "Orders Log",
                    "columns": [
                        {"name": "Order ID", "value": "{{order_id}}"},
                        {"name": "Customer", "value": "{{name}}"},
                        {"name": "Amount", "value": "{{amount}}"},
                        {"name": "Email", "value": "{{email}}"}
                    ]
                },
                "requiresApproval": False
            }
        ],
        "edges": [
            {"id": "e1", "source": "start-1", "target": "email-1"},
            {"id": "e2", "source": "email-1", "target": "sheet-1"}
        ]
    }


def _template_invoice_workflow() -> dict:
    return {
        "workflowName": "Invoice & Payment Collection",
        "summary": "When you need to invoice a customer, Aivaro will create and send a Stripe invoice, then follow up if unpaid.",
        "nodes": [
            {
                "id": "start-1",
                "type": "start_manual",
                "label": "When you start this workflow",
                "position": {"x": 250, "y": 50},
                "parameters": {},
                "requiresApproval": False
            },
            {
                "id": "stripe-1",
                "type": "stripe_create_invoice",
                "label": "Create Stripe invoice",
                "position": {"x": 250, "y": 200},
                "parameters": {
                    "customer_email": "{{email}}",
                    "amount": "{{amount}}",
                    "description": "{{service}} - {{description}}",
                    "due_days": 30,
                    "auto_send": "true"
                },
                "requiresApproval": True
            },
            {
                "id": "sheet-1",
                "type": "append_row",
                "label": "Log invoice",
                "position": {"x": 250, "y": 350},
                "parameters": {
                    "spreadsheet": "Invoices Log",
                    "columns": [
                        {"name": "Date", "value": "{{today}}"},
                        {"name": "Invoice ID", "value": "{{invoice_id}}"},
                        {"name": "Customer", "value": "{{name}}"},
                        {"name": "Amount", "value": "{{amount}}"},
                        {"name": "Status", "value": "Sent"}
                    ]
                },
                "requiresApproval": False
            },
            {
                "id": "delay-1",
                "type": "delay",
                "label": "Wait 7 days",
                "position": {"x": 250, "y": 500},
                "parameters": {
                    "duration": 7,
                    "unit": "days"
                },
                "requiresApproval": False
            },
            {
                "id": "email-1",
                "type": "send_email",
                "label": "Send payment reminder",
                "position": {"x": 250, "y": 650},
                "parameters": {
                    "to": "{{email}}",
                    "subject": "Payment Reminder - Invoice #{{invoice_id}}",
                    "body": "Hi {{name}},\n\nThis is a friendly reminder that your invoice for ${{amount}} is due soon.\n\nYou can pay here: {{invoice_url}}\n\nThank you!"
                },
                "requiresApproval": True
            }
        ],
        "edges": [
            {"id": "e1", "source": "start-1", "target": "stripe-1"},
            {"id": "e2", "source": "stripe-1", "target": "sheet-1"},
            {"id": "e3", "source": "sheet-1", "target": "delay-1"},
            {"id": "e4", "source": "delay-1", "target": "email-1"}
        ]
    }


def _template_report_workflow() -> dict:
    return {
        "workflowName": "Weekly Profit Report",
        "summary": "Every Monday, Aivaro will read your bookings spreadsheet, summarize the data with AI, and email you a profit report.",
        "nodes": [
            {
                "id": "start-1",
                "type": "start_schedule",
                "label": "Every Monday at 9am",
                "position": {"x": 250, "y": 50},
                "parameters": {
                    "time": "09:00",
                    "frequency": "weekly"
                },
                "requiresApproval": False
            },
            {
                "id": "read-1",
                "type": "read_sheet",
                "label": "Read bookings data",
                "position": {"x": 250, "y": 200},
                "parameters": {
                    "spreadsheet_id": "{{spreadsheet_id}}",
                    "range": "Sheet1!A1:G100"
                },
                "requiresApproval": False
            },
            {
                "id": "ai-1",
                "type": "ai_summarize",
                "label": "AI analyze weekly data",
                "position": {"x": 250, "y": 350},
                "parameters": {
                    "source": "bookings data",
                    "format": "bullet_points"
                },
                "requiresApproval": False
            },
            {
                "id": "email-1",
                "type": "send_email",
                "label": "Send weekly report",
                "position": {"x": 250, "y": 500},
                "parameters": {
                    "to": "{{your_email}}",
                    "subject": "Weekly Profit Report - Week of {{week_start}}",
                    "body": "Here's your weekly business summary:\n\n{{summary}}\n\n---\nGenerated by Aivaro"
                },
                "requiresApproval": False
            },
            {
                "id": "notify-1",
                "type": "send_notification",
                "label": "Notify report sent",
                "position": {"x": 250, "y": 650},
                "parameters": {
                    "message": "Weekly profit report has been generated and sent"
                },
                "requiresApproval": False
            }
        ],
        "edges": [
            {"id": "e1", "source": "start-1", "target": "read-1"},
            {"id": "e2", "source": "read-1", "target": "ai-1"},
            {"id": "e3", "source": "ai-1", "target": "email-1"},
            {"id": "e4", "source": "email-1", "target": "notify-1"}
        ]
    }


def _template_generic_workflow(prompt: str) -> dict:
    return {
        "workflowName": "Custom Automation",
        "summary": f"When triggered, Aivaro will execute your custom workflow.",
        "nodes": [
            {
                "id": "start-1",
                "type": "start_manual",
                "label": "When you start this workflow",
                "position": {"x": 250, "y": 50},
                "parameters": {},
                "requiresApproval": False
            },
            {
                "id": "notify-1",
                "type": "send_notification",
                "label": "Send notification",
                "position": {"x": 250, "y": 200},
                "parameters": {
                    "message": "Workflow completed successfully"
                },
                "requiresApproval": False
            }
        ],
        "edges": [
            {"id": "e1", "source": "start-1", "target": "notify-1"}
        ]
    }


def suggest_node_params(node_type: str, user_goal: str, sample_data: Optional[dict] = None) -> dict:
    """Suggest parameters for a node based on context"""
    
    suggestions = {
        "send_email": {
            "to": "{{email}}",
            "subject": "Your subject here",
            "body": "Hi {{name}},\n\nYour message here.\n\nBest regards"
        },
        "append_row": {
            "spreadsheet": "My Spreadsheet",
            "columns": [
                {"name": "Date", "value": "{{date}}"},
                {"name": "Name", "value": "{{name}}"},
                {"name": "Details", "value": "{{details}}"}
            ]
        },
        "delay": {
            "duration": 24,
            "unit": "hours"
        },
        "send_notification": {
            "message": "Something happened: {{details}}"
        }
    }
    
    return suggestions.get(node_type, {})
