"""
Agent Executor - LLM-driven autonomous task execution.

Instead of walking a static DAG, an LLM agent decides what to do next
at each step, using the user's connected integrations as tools.

This is what makes Aivaro genuinely agentic: the AI reasons at runtime,
adapts to results, and chains actions dynamically.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Any, AsyncGenerator, Optional
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Execution, ExecutionNode, Connection, Workflow, User
from app.services.node_executor import NodeExecutor, _interpolate
from app.utils.timezone import now_local

settings = get_settings()
logger = logging.getLogger(__name__)

# Max iterations to prevent runaway agents
MAX_AGENT_STEPS = 15
# Max consecutive failures before aborting
MAX_CONSECUTIVE_FAILURES = 3


# ---------------------------------------------------------------------------
# Tool definitions exposed to the LLM agent
# Each maps directly to a NodeExecutor method
# ---------------------------------------------------------------------------

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email via the user's connected Gmail. Use for confirmations, follow-ups, invoices, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "body": {"type": "string", "description": "Email body (plain text)"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_sms",
            "description": "Send an SMS text message via Twilio. Use for appointment reminders, confirmations, payment nudges.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Phone number (e.g. +15551234567)"},
                    "body": {"type": "string", "description": "SMS message text (keep under 160 chars when possible)"},
                },
                "required": ["to", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_whatsapp",
            "description": "Send a WhatsApp message via Twilio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Phone number"},
                    "body": {"type": "string", "description": "Message text"},
                },
                "required": ["to", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "make_call",
            "description": "Make an outbound phone call that speaks a message. Use for urgent reminders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Phone number"},
                    "message": {"type": "string", "description": "Message to speak on the call"},
                },
                "required": ["to", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a Google Calendar event.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Event title"},
                    "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                    "start_time": {"type": "string", "description": "Start time (HH:MM, 24h)"},
                    "duration": {"type": "number", "description": "Duration in hours (default 1)"},
                    "description": {"type": "string", "description": "Event description/notes"},
                    "location": {"type": "string", "description": "Location"},
                },
                "required": ["title", "date", "start_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_payment_link",
            "description": "Create a Stripe payment link for deposits or payments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount in dollars (e.g. 20.00)"},
                    "product_name": {"type": "string", "description": "What the payment is for (e.g. 'Booking Deposit')"},
                    "success_message": {"type": "string", "description": "Message shown after payment"},
                },
                "required": ["amount", "product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_invoice",
            "description": "Create and optionally send a Stripe invoice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_email": {"type": "string", "description": "Customer email"},
                    "amount": {"type": "number", "description": "Amount in dollars"},
                    "description": {"type": "string", "description": "Invoice line item description"},
                    "due_days": {"type": "integer", "description": "Days until due (default 30)"},
                    "auto_send": {"type": "boolean", "description": "Send immediately (default true)"},
                },
                "required": ["customer_email", "amount", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_spreadsheet_row",
            "description": "Add a row to a Google Spreadsheet. Use for logging bookings, tracking data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "spreadsheet": {"type": "string", "description": "Spreadsheet name"},
                    "sheet_name": {"type": "string", "description": "Sheet/tab name (default Sheet1)"},
                    "data": {
                        "type": "object",
                        "description": "Key-value pairs to add as a row (keys = column headers)",
                        "additionalProperties": {"type": "string"},
                    },
                },
                "required": ["spreadsheet", "data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_spreadsheet",
            "description": "Read data from a Google Spreadsheet. Use to look up bookings, check records.",
            "parameters": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID from the URL"},
                    "range": {"type": "string", "description": "Range to read (e.g. Sheet1!A1:Z100)"},
                },
                "required": ["spreadsheet_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_slack_message",
            "description": "Send a message to a Slack channel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Channel name (e.g. #general)"},
                    "message": {"type": "string", "description": "Message text"},
                },
                "required": ["channel", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "airtable_create_record",
            "description": "Create a record in an Airtable table.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_id": {"type": "string", "description": "Airtable base ID"},
                    "table_name": {"type": "string", "description": "Table name"},
                    "fields": {
                        "type": "object",
                        "description": "Field name -> value pairs",
                        "additionalProperties": {"type": "string"},
                    },
                },
                "required": ["base_id", "table_name", "fields"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "airtable_find_record",
            "description": "Find a record in Airtable by field value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_id": {"type": "string", "description": "Airtable base ID"},
                    "table_name": {"type": "string", "description": "Table name"},
                    "field_name": {"type": "string", "description": "Field to search"},
                    "field_value": {"type": "string", "description": "Value to match"},
                },
                "required": ["base_id", "table_name", "field_name", "field_value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "airtable_update_record",
            "description": "Update an existing Airtable record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_id": {"type": "string", "description": "Airtable base ID"},
                    "table_name": {"type": "string", "description": "Table name"},
                    "record_id": {"type": "string", "description": "Record ID to update"},
                    "fields": {
                        "type": "object",
                        "description": "Field name -> new value pairs",
                        "additionalProperties": {"type": "string"},
                    },
                },
                "required": ["base_id", "table_name", "record_id", "fields"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wait",
            "description": "Wait before taking the next action. Use for spacing out reminders or waiting for responses. Max 5 minutes in real-time; longer waits are simulated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration": {"type": "integer", "description": "Duration to wait"},
                    "unit": {"type": "string", "enum": ["seconds", "minutes", "hours"], "description": "Time unit"},
                    "reason": {"type": "string", "description": "Why you're waiting (shown to user)"},
                },
                "required": ["duration", "unit"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_calendar_events",
            "description": "List upcoming events from Google Calendar. Use to check appointments, find scheduling conflicts, or see what's coming up.",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_min": {"type": "string", "description": "Start of time range (ISO 8601, e.g. 2026-02-27T00:00:00Z). Defaults to now."},
                    "time_max": {"type": "string", "description": "End of time range (ISO 8601). Defaults to 7 days from now."},
                    "max_results": {"type": "integer", "description": "Max events to return (default 20)"},
                    "calendar_id": {"type": "string", "description": "Calendar ID (default: primary)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_emails",
            "description": "List recent emails from Gmail. Use to check for responses, find client messages, or look up information. Supports Gmail search syntax.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Gmail search query (e.g. 'from:john@example.com', 'subject:appointment', 'is:unread', 'newer_than:1d')"},
                    "max_results": {"type": "integer", "description": "Max messages to return (default 10)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_email",
            "description": "Get the full content of a specific email by its message ID. Use after list_emails to read a particular message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Gmail message ID (from list_emails results)"},
                },
                "required": ["message_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_payment",
            "description": "Check the status of a Stripe payment or look up recent payments by customer email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_email": {"type": "string", "description": "Customer email to look up payments for"},
                    "payment_intent_id": {"type": "string", "description": "Specific payment intent ID to check"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "airtable_list_records",
            "description": "List records from an Airtable table. Use to look up data, check records, or find information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_id": {"type": "string", "description": "Airtable base ID"},
                    "table_name": {"type": "string", "description": "Table name"},
                    "filter_formula": {"type": "string", "description": "Optional Airtable formula filter"},
                    "max_records": {"type": "integer", "description": "Max records to return"},
                },
                "required": ["base_id", "table_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark the task as complete. Call this when the goal has been achieved.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Brief summary of what was accomplished"},
                },
                "required": ["summary"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate to the user when you need input, approval, or can't proceed autonomously.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "Why you need human input"},
                    "question": {"type": "string", "description": "Specific question for the user"},
                },
                "required": ["reason"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Tool name -> NodeExecutor method mapping
# ---------------------------------------------------------------------------

TOOL_TO_NODE_TYPE = {
    "send_email": "send_email",
    "send_sms": "twilio_send_sms",
    "send_whatsapp": "twilio_send_whatsapp",
    "make_call": "twilio_make_call",
    "create_calendar_event": "google_calendar_create",
    "list_calendar_events": "google_calendar_list",
    "list_emails": "gmail_list_messages",
    "get_email": "gmail_get_message",
    "create_payment_link": "stripe_create_payment_link",
    "create_invoice": "stripe_create_invoice",
    "check_payment": "stripe_check_payment",
    "add_spreadsheet_row": "append_row",
    "read_spreadsheet": "read_sheet",
    "send_slack_message": "send_slack",
    "airtable_create_record": "airtable_create_record",
    "airtable_find_record": "airtable_find_record",
    "airtable_update_record": "airtable_update_record",
    "airtable_list_records": "airtable_list_records",
    "wait": "delay",
}


def _build_node_params(tool_name: str, args: dict) -> dict:
    """
    Convert agent tool arguments to NodeExecutor parameter format.
    The NodeExecutor expects parameters in a specific shape per node type.
    """
    if tool_name == "send_email":
        return {"to": args["to"], "subject": args["subject"], "body": args["body"]}

    if tool_name == "send_sms":
        return {"to": args["to"], "body": args["body"]}

    if tool_name == "send_whatsapp":
        return {"to": args["to"], "body": args["body"]}

    if tool_name == "make_call":
        return {"to": args["to"], "message": args["message"]}

    if tool_name == "create_calendar_event":
        return {
            "title": args["title"],
            "date": args["date"],
            "start_time": args["start_time"],
            "duration": args.get("duration", 1),
            "description": args.get("description", ""),
            "location": args.get("location", ""),
        }

    if tool_name == "create_payment_link":
        return {
            "amount": args["amount"],
            "product_name": args["product_name"],
            "success_message": args.get("success_message", "Thank you for your payment!"),
        }

    if tool_name == "create_invoice":
        return {
            "customer_email": args["customer_email"],
            "amount": args["amount"],
            "description": args["description"],
            "due_days": args.get("due_days", 30),
            "auto_send": args.get("auto_send", True),
        }

    if tool_name == "add_spreadsheet_row":
        data = args.get("data", {})
        return {
            "spreadsheet": args["spreadsheet"],
            "sheet_name": args.get("sheet_name", "Sheet1"),
            "columns": [{"name": k, "value": v} for k, v in data.items()],
        }

    if tool_name == "read_spreadsheet":
        return {
            "spreadsheet_id": args["spreadsheet_id"],
            "range": args.get("range", "Sheet1!A1:Z1000"),
        }

    if tool_name == "list_calendar_events":
        return {
            "time_min": args.get("time_min", ""),
            "time_max": args.get("time_max", ""),
            "max_results": args.get("max_results", 20),
            "calendar_id": args.get("calendar_id", "primary"),
        }

    if tool_name == "list_emails":
        return {
            "query": args.get("query", ""),
            "max_results": args.get("max_results", 10),
        }

    if tool_name == "get_email":
        return {"message_id": args["message_id"]}

    if tool_name == "check_payment":
        return {
            "customer_email": args.get("customer_email", ""),
            "payment_intent_id": args.get("payment_intent_id", ""),
        }

    if tool_name == "airtable_list_records":
        return args

    if tool_name == "send_slack_message":
        return {"channel": args["channel"], "message": args["message"]}

    if tool_name in ("airtable_create_record", "airtable_update_record", "airtable_find_record"):
        return args  # Already in the right shape

    if tool_name == "wait":
        return {"duration": args["duration"], "unit": args["unit"]}

    return args


# ---------------------------------------------------------------------------
# System prompt for the agent
# ---------------------------------------------------------------------------

def _build_agent_system_prompt(
    user: User,
    connections: dict[str, bool],
    context: Optional[dict] = None,
) -> str:
    """Build the system prompt that tells the agent who it is and what it can do."""

    local_now = now_local()
    time_str = local_now.strftime("%A, %B %d, %Y at %I:%M %p Pacific")

    # Build available tools summary based on connections
    available = []
    unavailable = []

    tool_connection_map = {
        "send_email": "google",
        "send_sms": "twilio",
        "send_whatsapp": "twilio",
        "make_call": "twilio",
        "create_calendar_event": "google",
        "list_calendar_events": "google",
        "list_emails": "google",
        "get_email": "google",
        "create_payment_link": "stripe",
        "create_invoice": "stripe",
        "check_payment": "stripe",
        "add_spreadsheet_row": "google",
        "read_spreadsheet": "google",
        "send_slack_message": "slack",
        "airtable_create_record": "airtable",
        "airtable_find_record": "airtable",
        "airtable_update_record": "airtable",
        "airtable_list_records": "airtable",
    }

    for tool_name, service in tool_connection_map.items():
        if connections.get(service):
            available.append(tool_name)
        else:
            unavailable.append(f"{tool_name} (needs {service})")

    # Always-available tools
    available.extend(["wait", "complete_task", "escalate_to_human"])

    available_str = ", ".join(available)
    unavailable_str = ", ".join(unavailable) if unavailable else "None"

    user_name = user.full_name or user.email.split("@")[0]

    context_block = ""
    if context:
        context_block = f"\n\nCONTEXT PROVIDED:\n{json.dumps(context, indent=2, default=str)}"

    return f"""You are an AI agent executing a task for {user_name}. You take real actions autonomously.

CURRENT TIME: {time_str}

AVAILABLE TOOLS: {available_str}
UNAVAILABLE (not connected): {unavailable_str}

RULES:
1. Execute the task step by step. After each tool call, evaluate the result and decide what to do next.
2. Be efficient - don't take unnecessary steps.
3. If a tool fails, try to recover (retry once, try alternate approach, or escalate).
4. When the task is complete, call complete_task with a summary.
5. If you can't proceed without user input, call escalate_to_human.
6. Never make up data. Use only what's provided in context or returned by tools.
7. For phone numbers, ensure they have country code (e.g. +1 for US).
8. For emails, use the actual addresses provided - never fabricate them.
9. Keep SMS messages concise (<160 chars when possible).
10. When sending confirmations or reminders, be professional and friendly.
11. DO NOT call tools that are unavailable - escalate instead.
12. In TEST MODE, tools simulate actions without actually sending. A result with "test_mode": true and success: true means the action was validated and WOULD work in production. Do NOT retry — move on to the next step.
{context_block}"""


# ---------------------------------------------------------------------------
# Agent Executor
# ---------------------------------------------------------------------------

class AgentExecutor:
    """
    Runs an LLM agent loop that autonomously executes a task
    using the user's connected integrations.
    """

    def __init__(
        self,
        db: Session,
        user: User,
        execution: Execution,
    ):
        self.db = db
        self.user = user
        self.execution = execution
        self.node_executor: Optional[NodeExecutor] = None
        self.connections_map: dict[str, bool] = {}
        self._step_count = 0

    def _load_connections(self) -> dict:
        """Load user's connection credentials."""
        connections = self.db.query(Connection).filter(
            Connection.user_id == self.user.id,
            Connection.is_connected == True,
        ).all()
        creds = {}
        for conn in connections:
            if conn.credentials:
                creds[conn.type] = conn.credentials
                self.connections_map[conn.type] = True
        return creds

    async def run(
        self,
        goal: str,
        context: Optional[dict] = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Execute the agent loop, yielding events as they happen.

        Events:
          {"type": "thinking", "content": "..."}
          {"type": "tool_start", "step": N, "tool": "...", "args": {...}}
          {"type": "tool_result", "step": N, "tool": "...", "success": bool, "output": {...}}
          {"type": "message", "content": "..."}  -- agent's reasoning/explanation
          {"type": "complete", "summary": "..."}
          {"type": "escalate", "reason": "...", "question": "..."}
          {"type": "error", "content": "..."}
        """
        # Initialize
        creds = self._load_connections()
        self.node_executor = NodeExecutor(connections=creds)

        try:
            async for event in self._agent_loop(goal, context):
                yield event
        finally:
            if self.node_executor:
                await self.node_executor.close()

    async def _agent_loop(
        self,
        goal: str,
        context: Optional[dict] = None,
    ) -> AsyncGenerator[dict, None]:
        """Core agent loop: LLM decides, we execute, repeat."""

        import openai

        if not settings.openai_api_key:
            yield {"type": "error", "content": "OpenAI API key not configured."}
            self.execution.status = "failed"
            self.db.commit()
            return

        client = openai.OpenAI(api_key=settings.openai_api_key)

        system_prompt = _build_agent_system_prompt(
            self.user, self.connections_map, context
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"TASK: {goal}"},
        ]

        yield {"type": "thinking", "content": f"Planning how to: {goal}"}

        consecutive_failures = 0
        completed_actions = []  # Track what's been done to prevent loops

        for iteration in range(MAX_AGENT_STEPS):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=AGENT_TOOLS,
                    tool_choice="auto",
                    temperature=0.3,  # Lower temp for reliable execution
                    max_tokens=1000,
                )
            except Exception as e:
                logger.error(f"[AgentExecutor] OpenAI error at step {iteration}: {e}")
                yield {"type": "error", "content": f"AI error: {str(e)}"}
                self.execution.status = "failed"
                self.db.commit()
                return

            choice = response.choices[0]

            # If the LLM wants to call tools
            if choice.message.tool_calls:
                messages.append(choice.message)

                for tool_call in choice.message.tool_calls:
                    fn_name = tool_call.function.name
                    try:
                        fn_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        fn_args = {}

                    self._step_count += 1

                    # --- Handle meta-tools ---
                    if fn_name == "complete_task":
                        summary = fn_args.get("summary", "Task completed.")
                        yield {"type": "complete", "summary": summary}
                        self._record_step(fn_name, fn_args, True, {"summary": summary})
                        self.execution.status = "completed"
                        self.execution.completed_at = datetime.utcnow()
                        self.db.commit()
                        return

                    if fn_name == "escalate_to_human":
                        reason = fn_args.get("reason", "Need input")
                        question = fn_args.get("question", "")
                        yield {"type": "escalate", "reason": reason, "question": question}
                        self._record_step(fn_name, fn_args, True, {"reason": reason})
                        self.execution.status = "paused"
                        self.db.commit()
                        # Provide tool response so LLM loop can end cleanly
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"escalated": True, "reason": reason}),
                        })
                        return

                    # --- Execute real tools via NodeExecutor ---
                    # Check for duplicate action (prevent loops)
                    action_key = f"{fn_name}:{json.dumps(fn_args, sort_keys=True)}"
                    if action_key in completed_actions:
                        # Already did this exact action — skip and tell LLM
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({
                                "success": True,
                                "already_completed": True,
                                "note": "This exact action was already completed successfully. Do NOT retry. Move on to the next step or call complete_task.",
                            }),
                        })
                        continue

                    yield {
                        "type": "tool_start",
                        "step": self._step_count,
                        "tool": fn_name,
                        "args": fn_args,
                    }

                    result = await self._execute_tool(fn_name, fn_args)
                    success = result.get("success", False)

                    yield {
                        "type": "tool_result",
                        "step": self._step_count,
                        "tool": fn_name,
                        "success": success,
                        "output": result.get("output", {}),
                        "logs": result.get("logs", ""),
                    }

                    self._record_step(fn_name, fn_args, success, result.get("output", {}))

                    if success:
                        consecutive_failures = 0
                        completed_actions.append(action_key)
                    else:
                        consecutive_failures += 1
                        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                            yield {
                                "type": "error",
                                "content": f"Too many consecutive failures ({MAX_CONSECUTIVE_FAILURES}). Stopping.",
                            }
                            self.execution.status = "failed"
                            self.db.commit()
                            return

                    # Feed result back to LLM
                    # Trim output to avoid blowing up context
                    result_summary = self._summarize_result(fn_name, result)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result_summary, default=str),
                    })

                continue  # Next LLM iteration

            # If the LLM responds with text (reasoning), capture it
            if choice.message.content:
                text = choice.message.content.strip()
                messages.append({"role": "assistant", "content": text})
                yield {"type": "message", "content": text}

            # If finish_reason is "stop" with no tool calls, the agent is done
            if choice.finish_reason == "stop" and not choice.message.tool_calls:
                # Agent stopped without calling complete_task — treat as implicit completion
                self.execution.status = "completed"
                self.execution.completed_at = datetime.utcnow()
                self.db.commit()
                yield {"type": "complete", "summary": "Task finished."}
                return

        # Hit max iterations
        yield {
            "type": "error",
            "content": f"Reached maximum steps ({MAX_AGENT_STEPS}). Task may be incomplete.",
        }
        self.execution.status = "failed"
        self.db.commit()

    async def _execute_tool(self, tool_name: str, args: dict) -> dict:
        """Route an agent tool call to the NodeExecutor."""
        node_type = TOOL_TO_NODE_TYPE.get(tool_name)
        if not node_type:
            return {
                "success": False,
                "output": {},
                "logs": f"Unknown tool: {tool_name}",
            }

        params = _build_node_params(tool_name, args)
        input_data = {}  # Agent provides everything via params

        try:
            result = await self.node_executor.execute(
                node_type=node_type,
                parameters=params,
                input_data=input_data,
                is_test=self.execution.is_test,
            )
            return result
        except Exception as e:
            logger.error(f"[AgentExecutor] Tool {tool_name} error: {e}")
            return {
                "success": False,
                "output": {},
                "logs": f"Error: {str(e)}",
            }

    def _record_step(
        self,
        tool_name: str,
        args: dict,
        success: bool,
        output: dict,
    ):
        """Record an execution step in the database."""
        exec_node = ExecutionNode(
            execution_id=self.execution.id,
            node_id=f"agent_step_{self._step_count}",
            node_type=f"agent:{tool_name}",
            node_label=self._tool_label(tool_name, args),
            status="completed" if success else "failed",
            input_data=args,
            output_data=output,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=0,
        )
        self.db.add(exec_node)
        self.execution.current_node_id = exec_node.node_id
        self.db.commit()

    def _tool_label(self, tool_name: str, args: dict) -> str:
        """Human-readable label for a tool call."""
        labels = {
            "send_email": lambda a: f"Email to {a.get('to', '?')}",
            "send_sms": lambda a: f"SMS to {a.get('to', '?')}",
            "send_whatsapp": lambda a: f"WhatsApp to {a.get('to', '?')}",
            "make_call": lambda a: f"Call {a.get('to', '?')}",
            "create_calendar_event": lambda a: f"Calendar: {a.get('title', '?')}",
            "list_calendar_events": lambda a: "Check calendar",
            "list_emails": lambda a: f"Check emails{' (' + a['query'] + ')' if a.get('query') else ''}",
            "get_email": lambda a: f"Read email {a.get('message_id', '?')[:8]}...",
            "create_payment_link": lambda a: f"Payment link ${a.get('amount', '?')}",
            "create_invoice": lambda a: f"Invoice ${a.get('amount', '?')} to {a.get('customer_email', '?')}",
            "check_payment": lambda a: f"Check payment for {a.get('customer_email', '?')}",
            "add_spreadsheet_row": lambda a: f"Row to {a.get('spreadsheet', '?')}",
            "read_spreadsheet": lambda a: "Read spreadsheet",
            "send_slack_message": lambda a: f"Slack to {a.get('channel', '?')}",
            "airtable_create_record": lambda a: f"Airtable record in {a.get('table_name', '?')}",
            "airtable_find_record": lambda a: f"Find in {a.get('table_name', '?')}",
            "airtable_update_record": lambda a: f"Update {a.get('table_name', '?')}",
            "airtable_list_records": lambda a: f"List {a.get('table_name', '?')}",
            "wait": lambda a: f"Wait {a.get('duration', '?')} {a.get('unit', '')}",
            "complete_task": lambda a: "Task complete",
            "escalate_to_human": lambda a: "Escalated to user",
        }
        fn = labels.get(tool_name, lambda a: tool_name)
        return fn(args)

    def _summarize_result(self, tool_name: str, result: dict) -> dict:
        """
        Create a concise result summary to feed back to the LLM.
        Prevents context window bloat from large outputs.
        """
        output = result.get("output", {})
        success = result.get("success", False)

        summary = {"success": success}

        # In test mode, clarify that "not sent" is expected
        logs = result.get("logs", "")
        if "[TEST]" in logs:
            summary["test_mode"] = True
            summary["note"] = "Action simulated (test mode) — this counts as successful."

        if not success:
            summary["error"] = logs[:500] if logs else "Unknown error"
            return summary

        # Include only the most relevant output fields
        important_keys = {
            "email_sent", "email_to", "email_subject", "message_id",
            "twilio_message_sid", "twilio_sms_sent", "twilio_whatsapp_sent",
            "twilio_call_sid", "twilio_call_made",
            "calendar_event_id", "calendar_event_url", "event_title",
            "calendar_events", "event_count",
            "emails", "email_count", "email",
            "payment_link_url", "payment_link_id",
            "invoice_id", "invoice_url", "invoice_status",
            "payment_status", "payment_amount", "payments",
            "row_added", "spreadsheet",
            "sheet_data", "row_count",
            "slack_sent",
            "airtable_record_id", "airtable_created", "airtable_found",
            "airtable_updated", "airtable_record", "airtable_records",
            "airtable_count",
            "simulated",
        }

        for key in important_keys:
            if key in output:
                val = output[key]
                # Truncate large values
                if isinstance(val, list) and len(val) > 10:
                    summary[key] = val[:10]
                    summary[f"{key}_truncated"] = True
                elif isinstance(val, str) and len(val) > 500:
                    summary[key] = val[:500] + "..."
                else:
                    summary[key] = val

        return summary


# ---------------------------------------------------------------------------
# Helper to create and run an agent execution
# ---------------------------------------------------------------------------

async def run_agent_task(
    db: Session,
    user: User,
    goal: str,
    context: Optional[dict] = None,
    is_test: bool = False,
    workflow_id: Optional[str] = None,
) -> AsyncGenerator[dict, None]:
    """
    High-level entry point: creates an Execution record and runs the agent.

    If workflow_id is provided, the execution is linked to that workflow.
    Otherwise a lightweight "agent task" workflow is created on the fly.
    """
    # Create or get workflow
    if not workflow_id:
        # Create a transient agent-task workflow
        workflow = Workflow(
            user_id=user.id,
            name=f"Agent: {goal[:50]}",
            description=goal,
            nodes=[],
            edges=[],
            is_active=False,
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        workflow_id = workflow.id

    # Create execution
    execution = Execution(
        workflow_id=workflow_id,
        status="running",
        is_test=is_test,
        trigger_data={"goal": goal, "context": context, "mode": "agent"},
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    agent = AgentExecutor(db=db, user=user, execution=execution)

    async for event in agent.run(goal=goal, context=context):
        yield event
