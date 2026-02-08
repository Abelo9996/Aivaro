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
        
        system_prompt = """You are a workflow automation assistant. Generate a workflow based on the user's description.

Return a JSON object with:
- workflowName: A short, descriptive name
- summary: A plain English sentence starting with "When... Aivaro will..."
- nodes: Array of nodes with {id, type, label, position: {x, y}, parameters, requiresApproval}
- edges: Array of edges with {id, source, target}

Available node types:
- start_manual: Manual start trigger
- start_form: Form submission trigger
- send_email: Send an email (requiresApproval: true by default)
- append_row: Add row to spreadsheet
- delay: Wait for a duration
- send_notification: Send a notification

Guidelines:
- Always start with a start node
- Create 3-6 steps
- No cycles
- Position nodes vertically, spaced 150px apart
- Mark email sending as requiresApproval: true
- Use friendly labels like "Send booking confirmation"

Return ONLY valid JSON, no markdown or explanation."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
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
        "workflowName": "New Booking Automation",
        "summary": "When a new booking is made, Aivaro will send a confirmation email and log it to your spreadsheet.",
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
                "id": "email-1",
                "type": "send_email",
                "label": "Send booking confirmation",
                "position": {"x": 250, "y": 200},
                "parameters": {
                    "to": "{{email}}",
                    "subject": "Your booking is confirmed!",
                    "body": "Hi {{name}},\n\nYour booking for {{service}} on {{booking_date}} at {{booking_time}} is confirmed.\n\nSee you soon!"
                },
                "requiresApproval": True
            },
            {
                "id": "sheet-1",
                "type": "append_row",
                "label": "Log to bookings spreadsheet",
                "position": {"x": 250, "y": 350},
                "parameters": {
                    "spreadsheet": "Bookings Log",
                    "columns": [
                        {"name": "Date", "value": "{{booking_date}}"},
                        {"name": "Time", "value": "{{booking_time}}"},
                        {"name": "Name", "value": "{{name}}"},
                        {"name": "Email", "value": "{{email}}"},
                        {"name": "Service", "value": "{{service}}"}
                    ]
                },
                "requiresApproval": False
            },
            {
                "id": "notify-1",
                "type": "send_notification",
                "label": "Notify you of new booking",
                "position": {"x": 250, "y": 500},
                "parameters": {
                    "message": "New booking: {{name}} for {{service}} on {{booking_date}}"
                },
                "requiresApproval": False
            }
        ],
        "edges": [
            {"id": "e1", "source": "start-1", "target": "email-1"},
            {"id": "e2", "source": "email-1", "target": "sheet-1"},
            {"id": "e3", "source": "sheet-1", "target": "notify-1"}
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
        "workflowName": "Overdue Invoice Follow-up",
        "summary": "When an invoice becomes overdue, Aivaro will send a reminder email.",
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
                "id": "email-1",
                "type": "send_email",
                "label": "Send payment reminder",
                "position": {"x": 250, "y": 200},
                "parameters": {
                    "to": "{{email}}",
                    "subject": "Payment Reminder - Invoice #{{invoice_id}}",
                    "body": "Hi {{name}},\n\nThis is a friendly reminder that invoice #{{invoice_id}} for ${{amount}} is now overdue.\n\nPlease arrange payment at your earliest convenience."
                },
                "requiresApproval": True
            },
            {
                "id": "sheet-1",
                "type": "append_row",
                "label": "Log reminder sent",
                "position": {"x": 250, "y": 350},
                "parameters": {
                    "spreadsheet": "Payment Reminders Log",
                    "columns": [
                        {"name": "Date", "value": "{{today}}"},
                        {"name": "Invoice", "value": "{{invoice_id}}"},
                        {"name": "Customer", "value": "{{name}}"},
                        {"name": "Amount", "value": "{{amount}}"}
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


def _template_report_workflow() -> dict:
    return {
        "workflowName": "Weekly Summary Report",
        "summary": "Aivaro will compile your weekly data and send you a summary report.",
        "nodes": [
            {
                "id": "start-1",
                "type": "start_manual",
                "label": "When you run this workflow",
                "position": {"x": 250, "y": 50},
                "parameters": {},
                "requiresApproval": False
            },
            {
                "id": "email-1",
                "type": "send_email",
                "label": "Send weekly summary",
                "position": {"x": 250, "y": 200},
                "parameters": {
                    "to": "{{your_email}}",
                    "subject": "Weekly Summary Report",
                    "body": "Here's your weekly summary:\n\n- Total sales: ${{total_sales}}\n- New customers: {{new_customers}}\n- Pending tasks: {{pending_tasks}}\n\nGreat work this week!"
                },
                "requiresApproval": False
            },
            {
                "id": "notify-1",
                "type": "send_notification",
                "label": "Notify report sent",
                "position": {"x": 250, "y": 350},
                "parameters": {
                    "message": "Weekly report has been generated and sent"
                },
                "requiresApproval": False
            }
        ],
        "edges": [
            {"id": "e1", "source": "start-1", "target": "email-1"},
            {"id": "e2", "source": "email-1", "target": "notify-1"}
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
