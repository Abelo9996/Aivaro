"""
LLM Chat Service for Aivaro
Provides two chat functionalities:
1. Execution Results Chat - Context-aware chat about specific workflow execution results
2. Global AI Assistant - Company-wide assistant with access to all workflows, executions, and company data
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Workflow, Execution, User

settings = get_settings()


def get_llm_client():
    """Get LLM client (OpenAI or fallback)"""
    if settings.openai_api_key:
        try:
            import openai
            return openai.OpenAI(api_key=settings.openai_api_key)
        except ImportError:
            return None
    return None


def build_execution_context(execution: Execution, workflow: Workflow) -> str:
    """Build context string for execution-specific chat"""
    context_parts = []
    
    # Workflow info
    context_parts.append(f"## Workflow: {workflow.name}")
    if workflow.description:
        context_parts.append(f"Description: {workflow.description}")
    if workflow.summary:
        context_parts.append(f"Summary: {workflow.summary}")
    
    # Workflow structure
    context_parts.append("\n## Workflow Steps:")
    for i, node in enumerate(workflow.nodes or [], 1):
        node_label = node.get('label', node.get('type', 'Unknown'))
        node_type = node.get('type', 'unknown')
        context_parts.append(f"{i}. {node_label} ({node_type})")
    
    # Execution info
    context_parts.append(f"\n## Execution Details:")
    context_parts.append(f"- Status: {execution.status}")
    context_parts.append(f"- Started: {execution.started_at}")
    if execution.completed_at:
        context_parts.append(f"- Completed: {execution.completed_at}")
    context_parts.append(f"- Test Run: {'Yes' if execution.is_test else 'No'}")
    
    # Trigger data
    if execution.trigger_data:
        context_parts.append("\n## Input Data:")
        context_parts.append(json.dumps(execution.trigger_data, indent=2, default=str))
    
    # Node execution results (from relationship)
    if execution.execution_nodes:
        context_parts.append("\n## Step Results:")
        spreadsheet_data = []
        
        for node_exec in execution.execution_nodes:
            node_info = f"- {node_exec.node_label or node_exec.node_id}: {node_exec.status}"
            context_parts.append(node_info)
            
            if node_exec.output_data:
                # Check for spreadsheet snapshot
                if "_spreadsheet_snapshot" in node_exec.output_data:
                    snapshot = node_exec.output_data["_spreadsheet_snapshot"]
                    spreadsheet_data.append(snapshot)
                
                # Show truncated output for regular data
                output_str = json.dumps(node_exec.output_data, default=str)
                if len(output_str) > 500:
                    context_parts.append(f"  Output: {output_str[:500]}...")
                else:
                    context_parts.append(f"  Output: {output_str}")
            if node_exec.logs:
                context_parts.append(f"  Logs: {node_exec.logs[:200]}")
        
        # Add full spreadsheet data section for chat queries
        if spreadsheet_data:
            context_parts.append("\n## Spreadsheet Data (Full):")
            for ss in spreadsheet_data:
                context_parts.append(f"\n### {ss.get('name', 'Sheet')}")
                context_parts.append(f"Read at: {ss.get('read_at', 'unknown')}")
                context_parts.append(f"Rows: {ss.get('row_count', 0)}, Columns: {ss.get('column_count', 0)}")
                
                data = ss.get("data", [])
                if data:
                    headers = data[0] if data else []
                    context_parts.append(f"Headers: {', '.join(str(h) for h in headers)}")
                    context_parts.append("\nData rows:")
                    
                    # Include all rows (up to reasonable limit for LLM context)
                    max_rows = 500  # Limit to prevent context overflow
                    for i, row in enumerate(data[1:max_rows+1], 1):
                        row_str = " | ".join(str(cell) for cell in row)
                        context_parts.append(f"  {i}. {row_str}")
                    
                    if len(data) > max_rows + 1:
                        context_parts.append(f"  ... and {len(data) - max_rows - 1} more rows")
    
    return "\n".join(context_parts)


def build_global_context(user: User, db: Session, include_executions: bool = True) -> str:
    """Build comprehensive context for global assistant"""
    context_parts = []
    
    # User/Company info
    context_parts.append("## Company/User Information:")
    context_parts.append(f"- User: {user.full_name or user.email}")
    if user.business_type:
        context_parts.append(f"- Business Type: {user.business_type}")
    
    # All workflows
    workflows = db.query(Workflow).filter(Workflow.user_id == user.id).all()
    context_parts.append(f"\n## Workflows ({len(workflows)} total):")
    
    for wf in workflows:
        wf_info = f"\n### {wf.name}"
        if wf.description:
            wf_info += f"\n{wf.description}"
        wf_info += f"\nActive: {'Yes' if wf.is_active else 'No'}"
        wf_info += f"\nSteps: {len(wf.nodes or [])}"
        
        # List node types
        node_types = [n.get('type', 'unknown') for n in (wf.nodes or [])]
        if node_types:
            wf_info += f"\nStep Types: {', '.join(node_types)}"
        
        context_parts.append(wf_info)
    
    # Recent executions
    if include_executions:
        recent_executions = db.query(Execution).filter(
            Execution.workflow_id.in_([w.id for w in workflows])
        ).order_by(Execution.started_at.desc()).limit(20).all()
        
        if recent_executions:
            context_parts.append(f"\n## Recent Executions ({len(recent_executions)} shown):")
            
            for exec in recent_executions:
                # Find workflow name
                wf = next((w for w in workflows if w.id == exec.workflow_id), None)
                wf_name = wf.name if wf else "Unknown"
                
                exec_info = f"- {wf_name}: {exec.status}"
                if exec.started_at:
                    exec_info += f" ({exec.started_at.strftime('%Y-%m-%d %H:%M')})"
                context_parts.append(exec_info)
    
    # Execution statistics
    total_executions = db.query(Execution).filter(
        Execution.workflow_id.in_([w.id for w in workflows])
    ).count()
    
    completed = db.query(Execution).filter(
        Execution.workflow_id.in_([w.id for w in workflows]),
        Execution.status == 'completed'
    ).count()
    
    failed = db.query(Execution).filter(
        Execution.workflow_id.in_([w.id for w in workflows]),
        Execution.status == 'failed'
    ).count()
    
    context_parts.append(f"\n## Statistics:")
    context_parts.append(f"- Total Workflows: {len(workflows)}")
    context_parts.append(f"- Total Executions: {total_executions}")
    context_parts.append(f"- Completed: {completed}")
    context_parts.append(f"- Failed: {failed}")
    if total_executions > 0:
        success_rate = (completed / total_executions) * 100
        context_parts.append(f"- Success Rate: {success_rate:.1f}%")
    
    return "\n".join(context_parts)


async def chat_about_execution(
    execution: Execution,
    workflow: Workflow,
    user_message: str,
    chat_history: List[Dict[str, str]] = None
) -> str:
    """Chat about a specific execution's results"""
    
    client = get_llm_client()
    context = build_execution_context(execution, workflow)
    
    system_prompt = f"""You are an AI assistant helping users understand their workflow execution results in Aivaro (a workflow automation tool like Zapier for non-technical users).

You have access to the following execution context:

{context}

Guidelines:
- Be helpful and explain results in plain English
- If asked about data, reference specific values from the execution
- **If the context includes Spreadsheet Data, you have access to the FULL spreadsheet contents.** You can answer questions about any data in the spreadsheet, perform calculations, find specific entries, summarize trends, etc.
- Suggest improvements or next steps based on the results
- If something failed, explain possible causes and fixes
- Keep responses concise but informative
- Use friendly, non-technical language when possible
- When discussing spreadsheet data, you can reference specific rows, columns, and values"""

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add chat history
    if chat_history:
        for msg in chat_history[-10:]:  # Last 10 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_message})
    
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM chat error: {e}")
            return _fallback_execution_response(execution, workflow, user_message)
    
    return _fallback_execution_response(execution, workflow, user_message)


async def chat_global_assistant(
    user: User,
    db: Session,
    user_message: str,
    chat_history: List[Dict[str, str]] = None
) -> str:
    """Global AI assistant with company-wide context"""
    
    client = get_llm_client()
    context = build_global_context(user, db)
    
    system_prompt = f"""You are Aivaro's AI assistant, helping {user.full_name or 'the user'} manage their workflow automations.

You have access to the following company context:

{context}

Your capabilities:
- Answer questions about any workflow or execution
- Suggest workflow improvements and optimizations
- Help troubleshoot issues
- Provide insights on automation performance
- Recommend new automations based on business needs
- Help users understand their data and results

Guidelines:
- Be proactive and suggest relevant insights
- Reference specific workflows and data when helpful
- Use friendly, non-technical language
- Offer actionable recommendations
- If asked about something not in context, explain what info you'd need"""

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add chat history
    if chat_history:
        for msg in chat_history[-15:]:  # Last 15 messages for more context
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_message})
    
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM chat error: {e}")
            return _fallback_global_response(user, user_message)
    
    return _fallback_global_response(user, user_message)


def _fallback_execution_response(execution: Execution, workflow: Workflow, user_message: str) -> str:
    """Fallback response when LLM is unavailable"""
    message_lower = user_message.lower()
    
    if "status" in message_lower or "result" in message_lower:
        if execution.status == "completed":
            return f"✅ Your workflow '{workflow.name}' completed successfully! All {len(workflow.nodes or [])} steps executed without issues."
        elif execution.status == "failed":
            return f"❌ The workflow '{workflow.name}' encountered an error. Check the step results above to see where it failed."
        else:
            return f"The workflow is currently in '{execution.status}' status."
    
    if "data" in message_lower or "output" in message_lower:
        if execution.trigger_data:
            return f"The workflow was triggered with this data:\n```\n{json.dumps(execution.trigger_data, indent=2)}\n```"
        return "No input data was provided for this execution."
    
    if "improve" in message_lower or "suggest" in message_lower:
        return "To improve this workflow, consider:\n1. Adding error handling with conditions\n2. Including notifications for failures\n3. Adding delays between email sends to avoid spam filters"
    
    return f"I can help you understand this execution of '{workflow.name}'. Ask me about:\n- The execution status and results\n- What data was processed\n- Suggestions for improvements\n- Why something may have failed"


def _fallback_global_response(user: User, user_message: str) -> str:
    """Fallback response when LLM is unavailable"""
    message_lower = user_message.lower()
    
    if "workflow" in message_lower:
        return "I can help you manage your workflows! To get more detailed AI assistance, please configure an OpenAI API key in your settings. In the meantime, check out the Workflows page to see all your automations."
    
    if "help" in message_lower:
        return """I'm your Aivaro AI assistant! I can help you with:
• Understanding your workflow results
• Suggesting improvements to your automations
• Answering questions about your data
• Troubleshooting issues

For full AI capabilities, configure an OpenAI API key in the settings."""
    
    return "I'm your Aivaro AI assistant! To unlock full conversational capabilities, please add an OpenAI API key in your settings. I can still help with basic questions about your workflows and executions."
