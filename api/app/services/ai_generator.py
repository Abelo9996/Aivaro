import json
from typing import Optional

from app.config import get_settings

settings = get_settings()


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
- start_email: Email received trigger (when an email arrives). Parameters: {from: "email@example.com"}

Available ACTION node types:
- send_email: Send an email. Parameters: {to: "{{from}}", subject: "Re: {{subject}}", body: "..."}
- ai_reply: Generate an AI response to an email. Parameters: {context: "...", tone: "professional/friendly/casual"}
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

IMPORTANT RULES:
1. For booking/appointment workflows with deposits → use google_calendar_create + stripe_create_payment_link
2. For payment reminders → use delay + stripe_check_payment + condition
3. For "when I receive an email from X" → use start_email trigger
4. For auto-reply workflows → use ai_reply node to generate smart responses
5. Available template variables: {{from}}, {{to}}, {{subject}}, {{email}}, {{name}}, {{date}}, {{time}}, {{amount}}, {{payment_link_url}}
6. Always connect nodes with edges
7. Position nodes vertically, starting at y=50, spaced 150px apart, x=250
8. Set requiresApproval: true for emails that need human review before sending

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
    
    # Detect workflow type based on keywords
    if any(word in prompt_lower for word in ["booking", "appointment", "schedule"]):
        return _template_booking_workflow()
    elif any(word in prompt_lower for word in ["lead", "follow up", "prospect"]):
        return _template_lead_followup()
    elif any(word in prompt_lower for word in ["order", "purchase", "receipt"]):
        return _template_order_workflow()
    elif any(word in prompt_lower for word in ["invoice", "payment", "overdue"]):
        return _template_invoice_workflow()
    elif any(word in prompt_lower for word in ["report", "summary", "daily", "weekly"]):
        return _template_report_workflow()
    else:
        return _template_generic_workflow(prompt)


def _template_booking_workflow() -> dict:
    return {
        "workflowName": "Booking with Deposit",
        "summary": "When a new booking is made, Aivaro will create a calendar event, generate a deposit payment link, send confirmation, and log it to your spreadsheet.",
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
                "requiresApproval": False
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
                "requiresApproval": False
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
                "requiresApproval": False
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
