"""
Agent Executor - LLM-driven autonomous task execution via MCP tool registry.

Instead of walking a static DAG, an LLM agent decides what to do next
at each step, using the user's connected integrations as MCP tools.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Any, AsyncGenerator, Optional
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Execution, ExecutionNode, Connection, Workflow, User
from app.utils.timezone import now_local

settings = get_settings()
logger = logging.getLogger(__name__)

# Max iterations to prevent runaway agents
MAX_AGENT_STEPS = 15
# Max consecutive failures before aborting
MAX_CONSECUTIVE_FAILURES = 3


# ---------------------------------------------------------------------------
# Meta-tools (always available, not MCP-routed)
# ---------------------------------------------------------------------------

META_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "wait",
            "description": "Wait before taking the next action. Use for spacing out reminders or waiting for responses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration": {"type": "integer", "description": "Duration to wait"},
                    "unit": {"type": "string", "enum": ["seconds", "minutes", "hours"], "description": "Time unit"},
                    "reason": {"type": "string", "description": "Why you're waiting"},
                },
                "required": ["duration", "unit"],
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

# Read-only tools don't count as "write actions" for billing
READ_ONLY_PREFIXES = {
    "gmail_list", "gmail_get", "google_calendar_list", "google_drive_list",
    "slack_list", "slack_read",
    "airtable_list", "airtable_find",
    "calendly_list", "calendly_get",
    "notion_search", "notion_query", "notion_get", "notion_list",
    "stripe_get", "stripe_list", "stripe_check",
    "mailchimp_list",
    "twilio_list",
}

META_TOOL_NAMES = {"wait", "complete_task", "escalate_to_human"}


def _is_read_only(tool_name: str) -> bool:
    """Check if a tool is read-only (doesn't count as a billable write action)."""
    if tool_name in META_TOOL_NAMES:
        return True
    return any(tool_name.startswith(prefix) for prefix in READ_ONLY_PREFIXES)


# ---------------------------------------------------------------------------
# System prompt builder
# ---------------------------------------------------------------------------

def _build_agent_system_prompt(
    user: User,
    available_tools: list[str],
    connected_providers: list[str],
    context: Optional[dict] = None,
    knowledge_context: str = "",
) -> str:
    """Build the system prompt that tells the agent who it is and what it can do."""

    local_now = now_local()
    time_str = local_now.strftime("%A, %B %d, %Y at %I:%M %p Pacific")

    user_name = user.full_name or user.email.split("@")[0]

    tools_str = ", ".join(available_tools) if available_tools else "None"
    providers_str = ", ".join(connected_providers) if connected_providers else "None"

    context_block = ""
    if context:
        context_block = f"\n\nCONTEXT PROVIDED:\n{json.dumps(context, indent=2, default=str)}"

    return f"""You are an AI agent executing a task for {user_name}. You take real actions autonomously.

CURRENT TIME: {time_str}

CONNECTED SERVICES: {providers_str}
AVAILABLE TOOLS: {tools_str}

RULES:
1. Execute the task step by step. After each tool call, evaluate the result and decide what to do next.
2. Be efficient - don't take unnecessary steps.
3. If a tool fails, try ONE more time only. If it fails again with the same error, escalate to the user immediately. NEVER retry more than once.
4. If a tool returns "not connected" or "connection not found", do NOT retry -- escalate immediately and tell the user which service needs to be connected.
5. When the task is complete, call complete_task with a summary.
6. If you can't proceed without user input, call escalate_to_human.
7. Never make up data. Use only what's provided in context or returned by tools.
8. For phone numbers, ensure they have country code (e.g. +1 for US).
9. For emails, use the actual addresses provided - never fabricate them.
10. Keep SMS messages concise (<160 chars when possible).
11. When sending confirmations or reminders, be professional and friendly.
12. DO NOT call tools that are unavailable - escalate instead.
13. In TEST MODE, tools simulate actions without actually sending. A result with "test_mode": true means the action was validated. Do NOT retry -- move on.
14. COMMUNICATION STYLE: Write in the business owner's natural voice based on the knowledge base. Don't write robotic templates -- write like a human would.
{context_block}
{knowledge_context}"""


# ---------------------------------------------------------------------------
# Agent Executor
# ---------------------------------------------------------------------------

class AgentExecutor:
    """
    Runs an LLM agent loop that autonomously executes a task
    using the user's connected integrations via MCP tool registry.
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
        self.registry = None  # MCPToolRegistry
        self._step_count = 0
        self.performed_write_action = False

    def _load_connections(self) -> dict:
        """Load user's connection credentials as {provider: creds_dict}."""
        connections = self.db.query(Connection).filter(
            Connection.user_id == self.user.id,
            Connection.is_connected == True,
        ).all()
        creds = {}
        for conn in connections:
            if conn.credentials:
                creds[conn.type] = conn.credentials
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
          {"type": "message", "content": "..."}
          {"type": "complete", "summary": "..."}
          {"type": "escalate", "reason": "...", "question": "..."}
          {"type": "error", "content": "..."}
        """
        from app.mcp_servers.registry import MCPToolRegistry

        creds = self._load_connections()
        self.registry = MCPToolRegistry(creds)

        try:
            async for event in self._agent_loop(goal, context):
                yield event
        finally:
            if self.registry:
                await self.registry.close()

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

        # Build tools list: MCP tools + meta tools
        mcp_tools = self.registry.list_all_tools()
        all_tools = mcp_tools + META_TOOLS
        all_tool_names = self.registry.list_all_tool_names() + list(META_TOOL_NAMES)

        # Get knowledge base context
        from app.services.knowledge_service import get_knowledge_context
        knowledge_ctx = get_knowledge_context(self.user.id, self.db)

        system_prompt = _build_agent_system_prompt(
            self.user,
            available_tools=all_tool_names,
            connected_providers=self.registry.connected_providers,
            context=context,
            knowledge_context=knowledge_ctx,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"TASK: {goal}"},
        ]

        yield {"type": "thinking", "content": f"Planning how to: {goal}"}

        consecutive_failures = 0
        completed_actions = []

        for iteration in range(MAX_AGENT_STEPS):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=all_tools,
                    tool_choice="auto",
                    temperature=0.3,
                    max_tokens=1000,
                )
            except Exception as e:
                logger.error(f"[AgentExecutor] OpenAI error at step {iteration}: {e}")
                yield {"type": "error", "content": f"AI error: {str(e)}"}
                self.execution.status = "failed"
                self.db.commit()
                return

            choice = response.choices[0]

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
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"escalated": True, "reason": reason}),
                        })
                        return

                    if fn_name == "wait":
                        duration = fn_args.get("duration", 1)
                        unit = fn_args.get("unit", "seconds")
                        reason = fn_args.get("reason", "")
                        secs = duration * {"seconds": 1, "minutes": 60, "hours": 3600}.get(unit, 1)
                        secs = min(secs, 300)  # Cap at 5 min
                        await asyncio.sleep(secs)
                        result_msg = {"waited": True, "duration": duration, "unit": unit, "reason": reason}
                        self._record_step(fn_name, fn_args, True, result_msg)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result_msg),
                        })
                        continue

                    # --- Check for duplicate action ---
                    action_key = f"{fn_name}:{json.dumps(fn_args, sort_keys=True)}"
                    if action_key in completed_actions:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({
                                "success": True,
                                "already_completed": True,
                                "note": "This exact action was already completed. Move on.",
                            }),
                        })
                        continue

                    # --- Execute via MCP registry ---
                    yield {
                        "type": "tool_start",
                        "step": self._step_count,
                        "tool": fn_name,
                        "args": fn_args,
                    }

                    if not self.registry.has_tool(fn_name):
                        result = {"error": f"Unknown tool: {fn_name}"}
                        success = False
                    else:
                        result = await self.registry.call_tool(fn_name, fn_args)
                        success = "error" not in result

                    if not _is_read_only(fn_name) and success:
                        self.performed_write_action = True

                    yield {
                        "type": "tool_result",
                        "step": self._step_count,
                        "tool": fn_name,
                        "success": success,
                        "output": result,
                    }

                    self._record_step(fn_name, fn_args, success, result)

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

                    # Feed result back to LLM (truncated)
                    result_str = json.dumps(result, default=str)
                    if len(result_str) > 3000:
                        result_str = result_str[:3000] + '..."}'
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_str,
                    })

                continue

            # Text response (reasoning)
            if choice.message.content:
                text = choice.message.content.strip()
                messages.append({"role": "assistant", "content": text})
                yield {"type": "message", "content": text}

            # Implicit completion
            if choice.finish_reason == "stop" and not choice.message.tool_calls:
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

    def _record_step(self, tool_name: str, args: dict, success: bool, output: dict):
        """Record an execution step in the database."""
        provider = ""
        if self.registry:
            provider = self.registry.get_provider_for_tool(tool_name) or ""

        exec_node = ExecutionNode(
            execution_id=self.execution.id,
            node_id=f"agent_step_{self._step_count}",
            node_type=f"agent:{tool_name}",
            node_label=f"{provider + ': ' if provider else ''}{tool_name}",
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


# ---------------------------------------------------------------------------
# Helper to create and run an agent execution
# ---------------------------------------------------------------------------

async def run_agent_task(
    db: Session,
    user: User,
    goal: str,
    context: Optional[dict] = None,
    workflow_id: Optional[str] = None,
) -> AsyncGenerator[dict, None]:
    """
    High-level entry point: creates an Execution record and runs the agent.
    """
    if not workflow_id:
        workflow = Workflow(
            user_id=user.id,
            name=f"Agent: {goal[:50]}",
            description=goal,
            nodes=[],
            edges=[],
            is_active=False,
            is_agent_task=True,
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        workflow_id = workflow.id

    execution = Execution(
        workflow_id=workflow_id,
        status="running",
        trigger_data={"goal": goal, "context": context, "mode": "agent"},
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    agent = AgentExecutor(db=db, user=user, execution=execution)

    async for event in agent.run(goal=goal, context=context):
        yield event

    if agent.performed_write_action:
        from app.services.plan_limits import increment_run_count
        increment_run_count(user, db)
