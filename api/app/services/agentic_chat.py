"""
Streaming Agentic Chat for Aivaro
Uses SSE (Server-Sent Events) to stream progress steps to the frontend
as the AI thinks and executes tools in real-time.
"""

import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Optional, Dict, Any, AsyncGenerator
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Workflow, Execution, Connection, ChatMessage, User
from app.services.ai_generator import generate_workflow_from_prompt

settings = get_settings()
logger = logging.getLogger(__name__)


# --- OpenAI Function Definitions ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_workflow",
            "description": "Create a new automated workflow from a plain-English description. Use this when the user asks to automate something, set up a workflow, or build an automation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "A clear description of what the workflow should do"
                    },
                    "name": {
                        "type": "string",
                        "description": "A short name for the workflow"
                    }
                },
                "required": ["description", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_workflows",
            "description": "List the user's existing workflows with their status.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_workflow_details",
            "description": "Get detailed information about a specific workflow.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string", "description": "Name or partial name of the workflow"}
                },
                "required": ["workflow_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_connections",
            "description": "Check which tools/services the user has connected.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_execution_summary",
            "description": "Get a summary of recent workflow executions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "activate_workflow",
            "description": "Activate a workflow so it runs automatically.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string"}
                },
                "required": ["workflow_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deactivate_workflow",
            "description": "Deactivate (pause) a workflow.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string"}
                },
                "required": ["workflow_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_webhook_url",
            "description": "Get the webhook/form URL for a workflow that has a form or webhook trigger. Use this when users ask how to connect their form, how the trigger works, or how to test a workflow.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string", "description": "Name or partial name of the workflow"}
                },
                "required": ["workflow_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_step_info",
            "description": "Get detailed information about what a specific workflow step type does, what it needs to work, and how to configure it. Use when users ask 'how does this step work?', 'what does this need?', or ask about a specific step type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "step_type": {
                        "type": "string",
                        "description": "The step type (e.g. start_form, send_email, google_calendar_create, stripe_create_payment_link, stripe_create_invoice, append_row, delay, ai_reply, slack_send_message, twilio_send_sms, twilio_send_whatsapp, twilio_make_call, airtable_create_record, airtable_update_record, airtable_list_records, airtable_find_record, etc.)"
                    }
                },
                "required": ["step_type"]
            }
        }
    },
]

# Human-friendly labels for tool calls
TOOL_LABELS = {
    "create_workflow": "Creating your workflow",
    "list_workflows": "Looking up your workflows",
    "get_workflow_details": "Getting workflow details",
    "list_connections": "Checking your connected tools",
    "get_execution_summary": "Reviewing recent runs",
    "activate_workflow": "Activating workflow",
    "deactivate_workflow": "Pausing workflow",
    "get_webhook_url": "Getting your form/webhook URL",
    "get_step_info": "Looking up step details",
}


# Map node types to required service connections + user-facing details
NODE_REQUIREMENTS = {
    "start_form": {
        "service": None,
        "description": "Built-in form trigger — no external connection needed",
        "user_setup": "Once activated, your workflow gets a unique webhook URL. You can embed it in your website form, share it as a booking link, or connect it to Typeform/Webflow. Any form POST to that URL triggers the workflow.",
        "data_provided": ["name", "email", "phone", "message", "any custom form fields"],
        "parameters": {},
    },
    "start_manual": {
        "service": None,
        "description": "Manual trigger — click 'Run' to start",
        "user_setup": "No setup needed. Click 'Run' on the workflow page to trigger it manually.",
        "data_provided": [],
        "parameters": {},
    },
    "start_schedule": {
        "service": None,
        "description": "Runs on a schedule (daily, weekly, monthly)",
        "user_setup": "Set the time and frequency. The workflow runs automatically on schedule.",
        "data_provided": [],
        "parameters": {"time": "e.g. 09:00", "frequency": "daily/weekly/monthly"},
    },
    "start_email": {
        "service": "gmail",
        "description": "Triggers when an email matching criteria arrives in your Gmail",
        "user_setup": "Connect your Gmail account. Set subject/sender filters. The workflow monitors your inbox and fires when a matching email arrives.",
        "data_provided": ["from", "subject", "body", "date"],
        "parameters": {"subject": "keyword to match", "from": "optional sender filter"},
    },
    "send_email": {
        "service": "gmail",
        "description": "Sends an email from your connected Gmail account",
        "user_setup": "Connect Gmail. Emails are sent as you. You can use {{variables}} from previous steps (e.g. {{email}}, {{name}}).",
        "data_provided": [],
        "parameters": {"to": "recipient (can use {{email}})", "subject": "email subject", "body": "email body with {{variables}}"},
    },
    "ai_reply": {
        "service": "gmail",
        "description": "AI generates and sends a reply to an email",
        "user_setup": "Connect Gmail. AI drafts a reply based on context you provide. You can set the tone.",
        "data_provided": ["generated reply text"],
        "parameters": {"context": "instructions for the AI", "tone": "professional/friendly/casual"},
    },
    "send_notification": {
        "service": None,
        "description": "Sends an in-app notification — no external service needed",
        "user_setup": "No setup. Notifications appear in your Aivaro dashboard.",
        "data_provided": [],
        "parameters": {"message": "notification text with {{variables}}"},
    },
    "append_row": {
        "service": "google_sheets",
        "description": "Adds a row to a Google Spreadsheet",
        "user_setup": "Connect Google Sheets. Specify which spreadsheet and sheet. Data from previous steps ({{name}}, {{email}}, etc.) auto-fills columns.",
        "data_provided": [],
        "parameters": {"spreadsheet": "spreadsheet name or ID", "sheet_name": "e.g. Sheet1", "columns": "list of {name, value} pairs"},
    },
    "google_calendar_create": {
        "service": "google_calendar",
        "description": "Creates an event in your Google Calendar",
        "user_setup": "Connect Google Calendar. Events are created in your primary calendar. Uses {{date}}, {{time}}, {{name}} from the trigger data.",
        "data_provided": ["event_id", "event_link"],
        "parameters": {"title": "event title", "date": "{{date}}", "start_time": "{{time}}", "duration": "hours", "description": "notes", "location": "address"},
    },
    "stripe_create_payment_link": {
        "service": "stripe",
        "description": "Creates a Stripe payment/deposit link",
        "user_setup": "Connect Stripe. A unique payment link is generated for each trigger. Payments go to your Stripe account. You set the amount and product name.",
        "data_provided": ["payment_link_url", "payment_link_id"],
        "parameters": {"amount": "dollar amount (e.g. 20)", "product_name": "e.g. 'Booking Deposit'", "success_message": "shown after payment"},
    },
    "stripe_check_payment": {
        "service": "stripe",
        "description": "Checks if a payment was completed",
        "user_setup": "Connect Stripe. Checks payment status for a given link/customer.",
        "data_provided": ["paid (true/false)", "amount_paid"],
        "parameters": {"payment_link_id": "{{payment_link_id}}", "customer_email": "{{email}}"},
    },
    "stripe_create_invoice": {
        "service": "stripe",
        "description": "Creates a Stripe invoice",
        "user_setup": "Connect Stripe. Invoice is created and optionally auto-sent to the customer.",
        "data_provided": ["invoice_id", "invoice_url"],
        "parameters": {"customer_email": "{{email}}", "amount": "dollar amount", "description": "line item", "due_days": "days until due", "auto_send": "true/false"},
    },
    "stripe_send_invoice": {
        "service": "stripe",
        "description": "Sends an existing Stripe invoice",
        "user_setup": "Connect Stripe. Sends a previously created invoice.",
        "data_provided": [],
        "parameters": {"invoice_id": "{{invoice_id}}"},
    },
    "stripe_get_customer": {
        "service": "stripe",
        "description": "Gets or creates a Stripe customer record",
        "user_setup": "Connect Stripe. Finds existing customer by email or creates a new one.",
        "data_provided": ["customer_id"],
        "parameters": {"email": "{{email}}", "name": "{{name}}"},
    },
    "delay": {
        "service": None,
        "description": "Waits for a specified duration before continuing",
        "user_setup": "No setup. Set the wait time. Useful for follow-up reminders.",
        "data_provided": [],
        "parameters": {"duration": "number", "unit": "hours/minutes/days"},
    },
    "condition": {
        "service": None,
        "description": "Branches the workflow based on a condition",
        "user_setup": "No external setup. Define a condition like 'if {{status}} == approved'. The workflow takes different paths based on the result.",
        "data_provided": [],
        "parameters": {"condition": "e.g. if {{status}} == 'approved'"},
    },
    "send_slack": {
        "service": "slack",
        "description": "Sends a message to a Slack channel",
        "user_setup": "Connect Slack. Pick a channel. Message can include {{variables}}.",
        "data_provided": [],
        "parameters": {"channel": "#channel-name", "message": "text with {{variables}}"},
    },
    "http_request": {
        "service": None,
        "description": "Makes an HTTP API call to any external service",
        "user_setup": "No connection needed — just provide the URL and method. Useful for custom integrations.",
        "data_provided": ["response_body", "status_code"],
        "parameters": {"url": "API endpoint", "method": "GET/POST/PUT/DELETE"},
    },
    # ========== Twilio (SMS / WhatsApp / Voice) ==========
    "twilio_send_sms": {
        "service": "twilio",
        "description": "Sends an SMS text message via Twilio",
        "user_setup": "Connect Twilio with your Account SID, Auth Token, and a Twilio phone number. SMS is sent from that number.",
        "data_provided": ["twilio_message_sid", "twilio_sms_sent"],
        "parameters": {"to": "recipient phone (can use {{phone}})", "body": "message text with {{variables}}", "from_number": "optional — defaults to your Twilio number"},
    },
    "twilio_send_whatsapp": {
        "service": "twilio",
        "description": "Sends a WhatsApp message via Twilio",
        "user_setup": "Connect Twilio. Requires a Twilio WhatsApp-enabled number or sandbox. Messages sent via WhatsApp Business API.",
        "data_provided": ["twilio_message_sid", "twilio_whatsapp_sent"],
        "parameters": {"to": "recipient phone (can use {{phone}})", "body": "message text with {{variables}}", "media_url": "optional image/doc URL"},
    },
    "twilio_make_call": {
        "service": "twilio",
        "description": "Makes an outbound phone call via Twilio",
        "user_setup": "Connect Twilio. Call plays a spoken message or TwiML instructions.",
        "data_provided": ["twilio_call_sid", "twilio_call_made"],
        "parameters": {"to": "recipient phone (can use {{phone}})", "message": "text to speak on the call", "twiml_url": "optional URL returning TwiML"},
    },
    # ========== Airtable ==========
    "airtable_create_record": {
        "service": "airtable",
        "description": "Creates a new record in an Airtable table",
        "user_setup": "Connect Airtable. Specify the base and table. Field values can use {{variables}} from previous steps.",
        "data_provided": ["airtable_record_id", "airtable_created"],
        "parameters": {"base_id": "Airtable base ID", "table_name": "table name", "fields": "dict of field_name: value pairs"},
    },
    "airtable_update_record": {
        "service": "airtable",
        "description": "Updates an existing Airtable record",
        "user_setup": "Connect Airtable. Updates specific fields on a record by ID.",
        "data_provided": ["airtable_updated"],
        "parameters": {"base_id": "Airtable base ID", "table_name": "table name", "record_id": "record ID (can use {{airtable_record_id}})", "fields": "dict of field_name: value pairs"},
    },
    "airtable_list_records": {
        "service": "airtable",
        "description": "Lists records from an Airtable table with optional filters",
        "user_setup": "Connect Airtable. Can filter by formula, sort, and limit results.",
        "data_provided": ["airtable_records", "airtable_count"],
        "parameters": {"base_id": "Airtable base ID", "table_name": "table name", "filter_formula": "optional Airtable formula", "max_records": "optional limit"},
    },
    "airtable_find_record": {
        "service": "airtable",
        "description": "Finds a record in Airtable by matching a field value",
        "user_setup": "Connect Airtable. Searches for a record where a specific field matches a value.",
        "data_provided": ["airtable_record", "airtable_record_id", "airtable_found"],
        "parameters": {"base_id": "Airtable base ID", "table_name": "table name", "field_name": "field to search", "field_value": "value to match (can use {{variables}})"},
    },
}

def _get_user_connections(user: User, db: Session) -> dict:
    """Returns dict of service_type -> connection info"""
    connections = db.query(Connection).filter(Connection.user_id == user.id).all()
    return {c.type: {"name": c.name, "connected": c.is_connected} for c in connections}


# --- Tool Execution ---

def execute_tool(tool_name: str, arguments: dict, user: User, db: Session) -> str:
    if tool_name == "create_workflow":
        return _tool_create_workflow(arguments, user, db)
    elif tool_name == "list_workflows":
        return _tool_list_workflows(user, db)
    elif tool_name == "get_workflow_details":
        return _tool_get_workflow_details(arguments, user, db)
    elif tool_name == "list_connections":
        return _tool_list_connections(user, db)
    elif tool_name == "get_execution_summary":
        return _tool_get_execution_summary(arguments, user, db)
    elif tool_name == "activate_workflow":
        return _tool_toggle_workflow(arguments, user, db, activate=True)
    elif tool_name == "deactivate_workflow":
        return _tool_toggle_workflow(arguments, user, db, activate=False)
    elif tool_name == "get_webhook_url":
        return _tool_get_webhook_url(arguments, user, db)
    elif tool_name == "get_step_info":
        return _tool_get_step_info(arguments)
    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def _tool_create_workflow(args: dict, user: User, db: Session) -> str:
    try:
        description = args["description"]
        name = args.get("name", "New Workflow")
        result = generate_workflow_from_prompt(description)
        if not result or not result.get("nodes"):
            return json.dumps({"success": False, "error": "Failed to generate workflow."})
        workflow = Workflow(
            user_id=user.id,
            name=result.get("workflowName", name),
            description=result.get("summary", description),
            nodes=result.get("nodes", []),
            edges=result.get("edges", []),
            is_active=False,
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        # Check which connections each step needs
        user_connections = _get_user_connections(user, db)
        steps_with_reqs = []
        missing_connections = set()
        for n in result.get("nodes", []):
            ntype = n.get("type", "")
            req = NODE_REQUIREMENTS.get(ntype, {"service": None, "description": "Unknown step type"})
            service = req["service"]
            connected = False
            if service is None:
                connected = True  # No connection needed
            elif service in user_connections:
                connected = user_connections[service].get("connected", False)
            if service and not connected:
                missing_connections.add(service)
            steps_with_reqs.append({
                "type": ntype,
                "label": n.get("label", n.get("type", "Step")),
                "requires": service,
                "connected": connected,
                "requirement_description": req["description"],
            })

        return json.dumps({
            "success": True, "workflow_id": workflow.id,
            "workflow_name": workflow.name,
            "node_count": len(result.get("nodes", [])),
            "summary": result.get("summary", ""),
            "steps": steps_with_reqs,
            "missing_connections": list(missing_connections),
        })
    except Exception as e:
        logger.error(f"create_workflow error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_list_workflows(user: User, db: Session) -> str:
    workflows = db.query(Workflow).filter(Workflow.user_id == user.id).order_by(Workflow.updated_at.desc()).all()
    if not workflows:
        return json.dumps({"workflows": [], "message": "No workflows yet."})
    return json.dumps({"workflows": [
        {"name": w.name, "active": w.is_active, "steps": len(w.nodes or []),
         "updated": w.updated_at.strftime("%Y-%m-%d %H:%M") if w.updated_at else None}
        for w in workflows
    ], "count": len(workflows)})


def _tool_get_workflow_details(args: dict, user: User, db: Session) -> str:
    name_query = args.get("workflow_name", "").lower()
    workflows = db.query(Workflow).filter(Workflow.user_id == user.id).all()
    match = next((w for w in workflows if name_query in (w.name or "").lower()), None)
    if not match:
        return json.dumps({"error": f"No workflow found matching '{args.get('workflow_name')}'"})
    recent = db.query(Execution).filter(Execution.workflow_id == match.id).order_by(Execution.started_at.desc()).limit(5).all()
    return json.dumps({
        "name": match.name, "description": match.description, "active": match.is_active,
        "steps": [{"type": n.get("type"), "label": n.get("label", n.get("type"))} for n in (match.nodes or [])],
        "recent_executions": [{"status": e.status, "started": e.started_at.strftime("%Y-%m-%d %H:%M") if e.started_at else None} for e in recent]
    })


def _tool_list_connections(user: User, db: Session) -> str:
    connections = db.query(Connection).filter(Connection.user_id == user.id).all()
    if not connections:
        return json.dumps({"connections": [], "message": "No tools connected yet."})
    return json.dumps({"connections": [
        {"service": c.type, "name": c.name, "connected": c.is_connected} for c in connections
    ], "count": len(connections)})


def _tool_get_execution_summary(args: dict, user: User, db: Session) -> str:
    limit = args.get("limit", 10)
    wf_ids = [w.id for w in db.query(Workflow).filter(Workflow.user_id == user.id).all()]
    if not wf_ids:
        return json.dumps({"executions": [], "message": "No workflows yet."})
    workflows = {w.id: w.name for w in db.query(Workflow).filter(Workflow.user_id == user.id).all()}
    executions = db.query(Execution).filter(Execution.workflow_id.in_(wf_ids)).order_by(Execution.started_at.desc()).limit(limit).all()
    total = db.query(Execution).filter(Execution.workflow_id.in_(wf_ids)).count()
    completed = db.query(Execution).filter(Execution.workflow_id.in_(wf_ids), Execution.status == "completed").count()
    return json.dumps({
        "recent": [{"workflow": workflows.get(e.workflow_id), "status": e.status} for e in executions],
        "stats": {"total": total, "completed": completed, "success_rate": f"{(completed/total*100):.0f}%" if total > 0 else "N/A"}
    })


def _tool_toggle_workflow(args: dict, user: User, db: Session, activate: bool) -> str:
    name_query = args.get("workflow_name", "").lower()
    match = next((w for w in db.query(Workflow).filter(Workflow.user_id == user.id).all() if name_query in (w.name or "").lower()), None)
    if not match:
        return json.dumps({"error": f"No workflow found matching '{args.get('workflow_name')}'"})
    match.is_active = activate
    db.commit()
    return json.dumps({"success": True, "message": f"Workflow '{match.name}' {'activated' if activate else 'deactivated'}."})


def _tool_get_webhook_url(args: dict, user: User, db: Session) -> str:
    name_query = args.get("workflow_name", "").lower()
    match = next((w for w in db.query(Workflow).filter(Workflow.user_id == user.id).all() if name_query in (w.name or "").lower()), None)
    if not match:
        return json.dumps({"error": f"No workflow found matching '{args.get('workflow_name')}'"})
    
    nodes = match.nodes or []
    has_form_trigger = any(n.get("type") in ["start_form", "start_webhook"] for n in nodes)
    if not has_form_trigger:
        return json.dumps({"error": "This workflow doesn't have a form/webhook trigger.", "suggestion": "It uses a different trigger type."})
    
    api_url = settings.api_url or "http://localhost:8000"
    webhook_url = f"{api_url}/api/webhooks/trigger/{match.id}"
    
    return json.dumps({
        "workflow_name": match.name,
        "workflow_id": match.id,
        "webhook_url": webhook_url,
        "is_active": match.is_active,
        "method": "POST",
        "usage": {
            "html_form": f'<form action="{webhook_url}" method="POST"><input name="name" placeholder="Name"><input name="email" type="email" placeholder="Email"><input name="phone" placeholder="Phone"><button type="submit">Book Now</button></form>',
            "embed_on_website": f"Set your website form's action URL to: {webhook_url}",
            "typeform": "Add this URL in Typeform → Settings → Webhooks",
            "webflow": "Paste this URL in your Webflow form's Action field",
            "test_curl": f'curl -X POST "{webhook_url}" -H "Content-Type: application/json" -d \'{{"name":"John","email":"john@test.com","phone":"555-1234"}}\'',
            "share_link": "You can build a simple booking page that posts to this URL",
        },
        "note": "The workflow must be activated before it responds to submissions." if not match.is_active else "Workflow is active and listening for submissions.",
    })


def _tool_get_step_info(args: dict) -> str:
    step_type = args.get("step_type", "").lower().strip()
    info = NODE_REQUIREMENTS.get(step_type)
    if not info:
        # Try fuzzy match
        for key, val in NODE_REQUIREMENTS.items():
            if step_type in key or key in step_type:
                info = val
                step_type = key
                break
    if not info:
        return json.dumps({"error": f"Unknown step type: '{args.get('step_type')}'. Available types: {', '.join(NODE_REQUIREMENTS.keys())}"})
    
    return json.dumps({
        "step_type": step_type,
        "description": info["description"],
        "requires_connection": info["service"],
        "user_setup": info["user_setup"],
        "data_provided": info.get("data_provided", []),
        "parameters": info.get("parameters", {}),
    })

# --- System Prompt ---

def build_system_prompt(user: User, db: Session) -> str:
    name = user.full_name or user.email
    biz = f" who runs a {user.business_type} business" if user.business_type else ""
    wf_count = db.query(Workflow).filter(Workflow.user_id == user.id).count()
    
    # Get actual connections
    user_conns = _get_user_connections(user, db)
    if user_conns:
        conn_lines = []
        for svc, info in user_conns.items():
            status = "connected" if info["connected"] else "not connected"
            conn_lines.append(f"  - {svc}: {status}")
        conn_summary = "CONNECTED TOOLS:\n" + "\n".join(conn_lines)
    else:
        conn_summary = "CONNECTED TOOLS: None yet. User needs to connect tools at /app/connections."

    # Get recent execution stats
    from datetime import timedelta
    recent_cutoff = datetime.utcnow() - timedelta(days=7)
    recent_execs = db.query(Execution).join(Workflow).filter(
        Workflow.user_id == user.id,
        Execution.started_at >= recent_cutoff
    ).all()
    if recent_execs:
        total = len(recent_execs)
        completed = sum(1 for e in recent_execs if e.status == "completed")
        failed = sum(1 for e in recent_execs if e.status == "failed")
        exec_summary = f"RECENT ACTIVITY (last 7 days): {total} workflow runs ({completed} completed, {failed} failed)"
    else:
        exec_summary = "RECENT ACTIVITY: No workflow runs yet."

    return f"""You are Aivaro — an AI that builds and runs business automations. You're talking to {name}{biz}.

ACCOUNT: {wf_count} workflows.
{conn_summary}
{exec_summary}

YOU ARE THE PRODUCT. When someone says "automate my bookings," use create_workflow immediately. Don't describe what you'd do — do it.

RULES:
- Use tools provided. Don't just describe steps — execute them.
- Be confident: "I've created that" not "I can help you create that."
- Never mention Zapier, Make, n8n, or competitors.
- FORMATTING IS MANDATORY. Structure every response with markdown:
  - Use **bold** for workflow names and key actions.
  - After creating a workflow, ALWAYS list steps as a numbered list. Example:

Created **Booking Automation** with 4 steps:

1. **Form Trigger** — Fires when a new booking form is submitted
2. **Create Calendar Event** — Adds the appointment to Google Calendar
3. **Generate Deposit Link** — Creates a Stripe payment link for the deposit
4. **Send Confirmation** — Emails the client with booking details and payment link

Head to **Workflows** to review and activate it.

  - Never write a single run-on paragraph. Always break into structured pieces.

AFTER CREATING A WORKFLOW:
- Check which connections are missing from the tool result (missing_connections field).
- If connections are missing, tell the user exactly which ones they need to connect and why.
- Example: "To activate this, you'll need to connect **Google Calendar** and **Stripe** at [Connections](/app/connections)."
- Be specific: don't say "connect your tools" — say which tools.

WHEN ASKED ABOUT HOW A STEP WORKS:
- Use the get_step_info tool to look up exact details, then explain clearly.
- For **form triggers (start_form)**: The workflow gets a unique webhook URL. The user can embed it in their website, use it with Typeform/Webflow, or share it as a booking link. Any form POST to that URL triggers the workflow. Use get_webhook_url to give them the actual URL.
- For **email steps (send_email)**: Sends from their connected Gmail as them. Can use {{variables}} from previous steps.
- For **Stripe steps**: Payments/deposits go to their Stripe account. Payment links are generated per-trigger.
- For **Calendar steps**: Events created in their Google Calendar with data from the trigger.
- For **Sheets steps (append_row)**: Adds a row with data from previous steps. They specify which spreadsheet.
- For **SMS steps (twilio_send_sms)**: Sends a text message via Twilio. Great for appointment reminders, payment nudges, confirmations. Uses {{phone}} from the trigger. Requires Twilio connection.
- For **WhatsApp steps (twilio_send_whatsapp)**: Sends WhatsApp messages via Twilio. Same as SMS but via WhatsApp. Requires Twilio connection with WhatsApp-enabled number.
- For **Call steps (twilio_make_call)**: Makes an outbound phone call that speaks a message. Useful for urgent reminders. Requires Twilio connection.
- For **Airtable steps (airtable_create_record, airtable_update_record, airtable_list_records, airtable_find_record)**: Full CRUD on Airtable bases. Create records to log data, update records to change status, list/find records to look up info. Requires Airtable connection.
- Always explain what DATA flows between steps — e.g., a form trigger provides {{name}}, {{email}}, {{phone}} that later steps can use.

WHEN ASKED "HOW DOES THE FORM KNOW?" or "WHERE IS THE FORM?":
- Explain the webhook URL concept simply: "Your workflow has a unique URL. Any form that posts to it triggers the automation."
- Use get_webhook_url to give them the actual URL for their workflow.
- Offer concrete options: embed HTML form, connect Typeform, use Webflow, or they can build a booking page.
- If the workflow isn't activated yet, remind them to activate it first."""


# --- Streaming Chat ---

async def agentic_chat_stream(
    user: User,
    db: Session,
    user_message: str,
    conversation_id: str = None,
) -> AsyncGenerator[dict, None]:
    """
    Stream chat events as SSE. Events:
    - {"type": "thinking", "content": "..."}
    - {"type": "step", "index": 0, "label": "...", "status": "running"|"done"|"error"}
    - {"type": "message", "content": "...", "metadata": {...}}
    - {"type": "done"}
    """

    # Save user message
    db.add(ChatMessage(user_id=user.id, role="user", content=user_message, conversation_id=conversation_id))
    db.commit()

    # Auto-title: if conversation has <=1 messages, generate title from first user message
    if conversation_id:
        from app.models.chat import ChatConversation
        msg_count = db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation_id).count()
        if msg_count <= 1:
            title = user_message[:60].strip()
            if len(user_message) > 60:
                title += "..."
            convo = db.query(ChatConversation).filter(ChatConversation.id == conversation_id).first()
            if convo:
                convo.title = title
                db.commit()

    # Load conversation history (scoped to this conversation)
    if conversation_id:
        recent = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.desc()).limit(30).all()
    else:
        recent = db.query(ChatMessage).filter(
            ChatMessage.user_id == user.id
        ).order_by(ChatMessage.created_at.desc()).limit(30).all()
    recent.reverse()

    messages = [{"role": "system", "content": build_system_prompt(user, db)}]
    for m in recent:
        messages.append({"role": m.role, "content": m.content})
    # user_message is already in `recent` (saved above), don't duplicate

    client = _get_openai_client()
    if not client:
        fallback = _fallback_response(user, user_message)
        db.add(ChatMessage(user_id=user.id, role="assistant", content=fallback, conversation_id=conversation_id))
        db.commit()
        yield {"type": "message", "content": fallback}
        yield {"type": "done"}
        return

    yield {"type": "thinking", "content": "Understanding your request..."}

    step_index = 0
    collected_steps = []  # Collect steps for metadata persistence
    _executor = ThreadPoolExecutor(max_workers=2)

    def _call_openai(msgs):
        return client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1500,
        )

    for iteration in range(5):
        try:
            logger.info(f"[agentic] Iteration {iteration}, {len(messages)} messages in context")
            response = await asyncio.get_event_loop().run_in_executor(_executor, _call_openai, messages)
        except Exception as e:
            logger.error(f"OpenAI error on iteration {iteration}: {e}", exc_info=True)
            yield {"type": "step", "index": step_index, "label": "Something went wrong", "status": "error"}
            yield {"type": "message", "content": "Something went wrong on my end. Try again in a moment."}
            yield {"type": "done"}
            return

        choice = response.choices[0]
        logger.info(f"[agentic] finish_reason={choice.finish_reason}, has_tool_calls={bool(choice.message.tool_calls)}")

        if choice.message.tool_calls:
            messages.append(choice.message)

            for tool_call in choice.message.tool_calls:
                fn_name = tool_call.function.name
                try:
                    fn_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}

                label = TOOL_LABELS.get(fn_name, fn_name.replace("_", " ").title())

                # Add context to label
                if fn_name == "create_workflow" and fn_args.get("name"):
                    label = f'Creating "{fn_args["name"]}"'
                elif fn_name == "activate_workflow" and fn_args.get("workflow_name"):
                    label = f'Activating "{fn_args["workflow_name"]}"'

                yield {"type": "step", "index": step_index, "label": label, "status": "running"}

                result = await asyncio.get_event_loop().run_in_executor(
                    _executor, execute_tool, fn_name, fn_args, user, db
                )

                # Parse result for richer step info
                try:
                    result_data = json.loads(result)
                    if result_data.get("success") == False:
                        step_event = {"index": step_index, "label": label, "status": "error", "detail": result_data.get("error", "")}
                        collected_steps.append(step_event)
                        yield {"type": "step", **step_event}
                    else:
                        detail = ""
                        extra = {}
                        if fn_name == "create_workflow" and result_data.get("node_count"):
                            detail = f'{result_data["node_count"]} steps generated'
                            extra = {
                                "workflow_name": result_data.get("workflow_name", ""),
                                "workflow_id": result_data.get("workflow_id"),
                                "workflow_steps": result_data.get("steps", []),
                                "summary": result_data.get("summary", ""),
                                "missing_connections": result_data.get("missing_connections", []),
                            }
                        elif fn_name == "list_workflows":
                            detail = f'{result_data.get("count", 0)} workflows found'
                        elif fn_name == "list_connections":
                            detail = f'{result_data.get("count", 0)} tools connected'
                        step_event = {"index": step_index, "label": label, "status": "done", "detail": detail, **extra}
                        collected_steps.append(step_event)
                        yield {"type": "step", **step_event}
                except:
                    step_event = {"index": step_index, "label": label, "status": "done"}
                    collected_steps.append(step_event)
                    yield {"type": "step", **step_event}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
                step_index += 1

            continue

        # Final text response
        text = choice.message.content or ""
        metadata = {"steps": collected_steps} if collected_steps else None
        db.add(ChatMessage(
            user_id=user.id, role="assistant", content=text,
            conversation_id=conversation_id, metadata_json=metadata
        ))
        db.commit()
        yield {"type": "message", "content": text, "metadata": metadata}
        yield {"type": "done"}
        return

    yield {"type": "message", "content": "I got a bit lost. Could you rephrase?"}
    yield {"type": "done"}


# Also keep the non-streaming version for backwards compat
async def agentic_chat(user: User, db: Session, user_message: str, conversation_id: str = None) -> str:
    final_message = ""
    async for event in agentic_chat_stream(user, db, user_message, conversation_id=conversation_id):
        if event["type"] == "message":
            final_message = event["content"]
    return final_message


def _get_openai_client():
    if settings.openai_api_key:
        try:
            import openai
            return openai.OpenAI(api_key=settings.openai_api_key)
        except:
            return None
    return None


def _fallback_response(user: User, user_message: str) -> str:
    name = f", {user.full_name.split(' ')[0]}" if user.full_name else ""
    if any(w in user_message.lower() for w in ["create", "build", "set up", "automate", "make"]):
        return f"Hey{name}! I can build that, but I need an OpenAI API key configured to generate workflows. Once that's set, just tell me what to automate."
    return f"Hey{name}! I'm Aivaro — I build and run automations for your business. To unlock full capabilities, configure an OpenAI API key on the backend."
