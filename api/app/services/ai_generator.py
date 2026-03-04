import json
import logging
from typing import Optional, List, Dict, Any

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def _get_mcp_tool_docs(connected_providers: list[str] = None) -> str:
    """Generate documentation for MCP tools that aren't hardcoded in the system prompt.
    
    Only includes tools from connected providers. Returns a string block to append to the prompt.
    """
    # Providers already fully documented in the hardcoded prompt
    HARDCODED_PROVIDERS = {"google", "slack", "stripe", "twilio", "airtable", "notion", "calendly", "mailchimp"}
    
    from app.mcp_servers.registry import SERVER_FACTORIES
    
    # Determine which new providers to document
    if connected_providers:
        new_providers = [p for p in connected_providers if p not in HARDCODED_PROVIDERS and p in SERVER_FACTORIES]
    else:
        # If no connected_providers info, include all non-hardcoded
        new_providers = [p for p in SERVER_FACTORIES if p not in HARDCODED_PROVIDERS]
    
    if not new_providers:
        return ""
    
    # Fake creds to instantiate servers (just for schema — no API calls)
    fake_creds = {
        "access_token": "x", "api_key": "x", "account_sid": "x", "auth_token": "x",
        "phone_number": "x", "shop_domain": "x", "bot_token": "x", "guild_id": "x",
        "domain": "x", "email": "x", "api_token": "x", "phone_number_id": "x",
        "refresh_token": "x",
    }
    
    sections = []
    for provider in sorted(new_providers):
        factory = SERVER_FACTORIES.get(provider)
        if not factory:
            continue
        try:
            server = factory(fake_creds)
            tools = server.list_tools()
            if not tools:
                continue
            
            lines = [f"\n{provider.upper()} node types (user has {provider} connected):"]
            for t in tools:
                func_def = t.get("function", t)
                name = func_def.get("name", "")
                desc = func_def.get("description", "")
                params = func_def.get("parameters", {})
                props = params.get("properties", {})
                required = params.get("required", [])
                
                param_parts = []
                for pname, pdef in props.items():
                    pdesc = pdef.get("description", "")
                    req_marker = " (required)" if pname in required else ""
                    param_parts.append(f'{pname}: "{pdesc}"{req_marker}')
                
                param_str = ", ".join(param_parts) if param_parts else "no parameters"
                lines.append(f"- {name}: {desc}. Parameters: {{{param_str}}}")
            
            sections.append("\n".join(lines))
        except Exception as e:
            logger.warning(f"[ai_generator] Failed to get MCP tool docs for {provider}: {e}")
    
    if not sections:
        return ""
    
    return "\n\nADDITIONAL INTEGRATION NODE TYPES (from MCP):\nWhen these nodes follow a read_sheet node, row columns are available as {{column_name}} (lowercased, spaces→underscores). Fill parameters with these variables.\n" + "\n".join(sections) + "\n"


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
            model="gpt-4o",
            messages=[
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": f"Analyze this workflow request: {prompt}"}
            ],
            max_completion_tokens=8192
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


def generate_workflow_from_prompt(prompt: str, connected_providers: list[str] = None) -> dict:
    """Generate a workflow from a plain English prompt.
    
    Args:
        prompt: Plain English description of the workflow.
        connected_providers: List of connected provider names (e.g. ['google', 'slack', 'stripe']).
            Used to filter available node types and warn about missing connections.
    """
    
    # If OpenAI key is available, use it
    if settings.openai_api_key:
        result = _generate_with_openai(prompt, connected_providers=connected_providers)
    else:
        # Otherwise, use deterministic generator
        result = _generate_deterministic(prompt)
    
    # Always apply approval defaults
    if result and result.get("nodes"):
        result["nodes"] = apply_approval_defaults(result["nodes"])
    
    # Fix condition edges missing sourceHandle
    if result and result.get("nodes") and result.get("edges"):
        result["edges"] = fix_condition_edges(result["nodes"], result["edges"])
    
    # Prune unnecessary 'no' branch generic reply nodes
    if result and result.get("nodes") and result.get("edges"):
        result["nodes"], result["edges"] = prune_dead_no_branches(result["nodes"], result["edges"])
    
    # Validate and clean template variables
    if result and result.get("nodes") and result.get("edges"):
        result["nodes"] = validate_template_variables(result["nodes"], result["edges"])
    
    return result


# Node types that should require approval by default
APPROVAL_DEFAULT_NODES = {
    "send_email",
    "stripe_create_payment_link",
    "stripe_create_invoice",
    "stripe_send_invoice",
    "twilio_send_sms",
    "twilio_send_whatsapp",
    "twilio_make_call",
    "mailchimp_send_campaign",
    "approval",
    # MCP tools that send external communications
    "brevo_send_transactional_email",
    "brevo_send_sms",
    "brevo_send_whatsapp",
    "brevo_send_campaign_now",
    "brevo_create_email_campaign",
    "sendgrid_send_email",
    "sendgrid_send_template",
    "whatsapp_send_message",
    "whatsapp_send_template",
    "discord_send_message",
    "shopify_cancel_order",
}

# Node types that should never require approval
NO_APPROVAL_NODES = {
    "start_manual", "start_form", "start_webhook", "start_schedule", "start_email",
    "delay", "condition", "transform", "append_row", "read_sheet",
    "send_notification", "google_calendar_create", "google_calendar_list",
    "gmail_list_messages", "gmail_get_message",
    "airtable_create_record", "airtable_update_record", "airtable_list_records", "airtable_find_record",
    "notion_create_page", "notion_update_page", "notion_query_database", "notion_search",
    "calendly_list_events", "calendly_get_event", "calendly_cancel_event", "calendly_create_link",
    "mailchimp_add_subscriber", "mailchimp_update_subscriber", "mailchimp_add_tags",
    "ai_reply", "ai_summarize", "ai_extract",
    "send_slack", "slack_send_dm", "http_request",
    "email_template",
}


def fix_condition_edges(nodes: list, edges: list) -> list:
    """Ensure edges from condition nodes have sourceHandle='yes'/'no'.
    
    If a condition node has exactly 2 outgoing edges without sourceHandle,
    assign 'yes' to the first and 'no' to the second.
    """
    condition_ids = {n["id"] for n in nodes if n.get("type") == "condition"}
    if not condition_ids:
        return edges
    
    for cid in condition_ids:
        outgoing = [e for e in edges if e["source"] == cid]
        if len(outgoing) == 2 and not any(e.get("sourceHandle") for e in outgoing):
            outgoing[0]["sourceHandle"] = "yes"
            outgoing[1]["sourceHandle"] = "no"
            print(f"[AI Generator] Auto-fixed sourceHandle on edges from condition node {cid}")
    
    return edges


def prune_dead_no_branches(nodes: list, edges: list) -> tuple[list, list]:
    """Remove unnecessary 'no' branch nodes that just send generic replies.
    
    When a condition's 'no' branch leads to a single outbound node (send_email, 
    twilio_send_sms, etc.) with no further children, and the node's parameters
    are generic (using {{ai_response}} or similar), remove it. The default for
    non-matching conditions should be silence — not a random reply.
    
    Only keeps 'no' branches that:
    - Lead to 2+ nodes (a real workflow path)
    - Have specific, non-template content (explicit user-defined text)
    - Are non-outbound types (e.g., append_row, send_notification)
    """
    OUTBOUND_TYPES = {
        "send_email", "twilio_send_sms", "twilio_send_whatsapp", 
        "twilio_make_call", "slack_send_dm", "mailchimp_send_campaign",
        "send_slack", "discord_send_message", "sendgrid_send_email",
        "whatsapp_send_text",
    }
    GENERIC_BODY_MARKERS = {
        "{{ai_response}}", "{{ai_reply}}", "{{response}}", "{{reply}}",
        "{{message}}", "{{body}}", "{{content}}",
    }
    
    condition_ids = {n["id"] for n in nodes if n.get("type") == "condition"}
    if not condition_ids:
        return nodes, edges
    
    node_map = {n["id"]: n for n in nodes}
    nodes_to_remove = set()
    edges_to_remove = set()
    
    for cid in condition_ids:
        # Find "no" branch edges
        no_edges = [e for e in edges if e["source"] == cid and e.get("sourceHandle") == "no"]
        if not no_edges:
            continue
        
        for no_edge in no_edges:
            target_id = no_edge["target"]
            target_node = node_map.get(target_id)
            if not target_node:
                continue
            
            target_type = target_node.get("type", "")
            
            # Only prune outbound nodes
            if target_type not in OUTBOUND_TYPES:
                continue
            
            # Check if this node has children (a real path continues)
            children = [e for e in edges if e["source"] == target_id]
            if children:
                continue  # Has downstream nodes — this is a real branch, keep it
            
            # Check if the body/message is generic (template-only)
            params = target_node.get("parameters", {})
            body = params.get("body", params.get("message", ""))
            is_generic = any(marker in body for marker in GENERIC_BODY_MARKERS) or not body.strip()
            
            if is_generic:
                nodes_to_remove.add(target_id)
                edges_to_remove.add(no_edge["id"])
                print(f"[AI Generator] Pruned generic 'no' branch: {target_node.get('label', target_id)} (type: {target_type})")
    
    if nodes_to_remove:
        nodes = [n for n in nodes if n["id"] not in nodes_to_remove]
        edges = [e for e in edges if e["id"] not in edges_to_remove and e["source"] not in nodes_to_remove and e["target"] not in nodes_to_remove]
    
    return nodes, edges


def validate_template_variables(nodes: list, edges: list) -> list:
    """Validate and clean {{variable}} references in node parameters.
    
    Builds the set of variables each node CAN access (from trigger inputs +
    all upstream node outputs), then removes/replaces references to variables 
    that no upstream node produces and aren't in the known base set.
    """
    import re
    
    # Base variables always available from trigger/system
    BASE_VARIABLES = {
        # Email trigger
        "from", "to", "subject", "snippet", "body", "sender_email", "sender_name",
        "message_id",
        # Form trigger  
        "name", "email", "phone", "message",
        # System
        "user_email", "today", "date", "current_time", "timestamp", "timezone",
        # User info
        "first_name", "last_name", "full_name", "company", "company_name",
    }
    
    # Variables produced by specific node types
    NODE_OUTPUT_VARIABLES = {
        "ai_reply": {"ai_response", "response", "reply", "answer"},
        "ai_extract": {"customer_name", "customer_email", "requested_date", "requested_time",
                       "is_appointment", "service_type", "phone", "amount"},
        "ai_summarize": {"summary", "ai_response"},
        "condition": {"condition_result"},
        "stripe_create_payment_link": {"payment_link_url", "payment_link_id"},
        "stripe_create_invoice": {"invoice_id", "invoice_url"},
        "google_calendar_create": {"event_id", "event_link"},
        "calendly_create_link": {"calendly_link", "booking_url", "scheduling_url"},
        "calendly_list_events": {"calendly_events", "event_count", "calendly_count"},
        "airtable_create_record": {"record_id", "airtable_record_id"},
        "airtable_find_record": {"record_id", "record"},
        "notion_create_page": {"page_id", "notion_page_id", "page_url"},
        "notion_search": {"results", "page_id"},
        "append_row": {"row_number", "spreadsheet_url"},
        "read_sheet": {"rows", "data"},
    }
    
    # AI reply/extract can produce ANY variable the prompt asks for (dynamic)
    AI_DYNAMIC_TYPES = {"ai_reply", "ai_extract"}
    
    # Build node order (topological-ish based on edges)
    node_map = {n["id"]: n for n in nodes}
    edge_map = {}  # target -> [source nodes]
    for e in edges:
        edge_map.setdefault(e["target"], []).append(e["source"])
    
    def get_upstream_ids(nid, visited=None):
        if visited is None:
            visited = set()
        if nid in visited:
            return visited
        visited.add(nid)
        for src in edge_map.get(nid, []):
            get_upstream_ids(src, visited)
        return visited
    
    # Check if any upstream node is an AI type (can produce arbitrary vars)
    def has_upstream_ai(nid):
        upstream = get_upstream_ids(nid) - {nid}
        return any(node_map.get(uid, {}).get("type") in AI_DYNAMIC_TYPES for uid in upstream)
    
    def get_available_vars(nid):
        """Get all variables available to a node."""
        available = set(BASE_VARIABLES)
        upstream = get_upstream_ids(nid) - {nid}
        for uid in upstream:
            utype = node_map.get(uid, {}).get("type", "")
            if utype in NODE_OUTPUT_VARIABLES:
                available.update(NODE_OUTPUT_VARIABLES[utype])
        return available
    
    # Patterns that are clearly fake/hallucinated
    FAKE_PATTERNS = re.compile(
        r'calendly_event_link|booking_link|confirmation_link|'
        r'payment_url|invoice_link|scheduling_link|'
        r'calendar_link|event_url|meeting_link|'
        r'zoom_link|zoom_url|google_meet_link',
        re.IGNORECASE
    )
    
    modified = False
    for node in nodes:
        params = node.get("parameters", {})
        if not params:
            continue
        
        nid = node["id"]
        available = get_available_vars(nid)
        upstream_has_ai = has_upstream_ai(nid)
        
        for key, value in list(params.items()):
            if not isinstance(value, str) or "{{" not in value:
                continue
            
            vars_in_value = re.findall(r'\{\{([^}]+)\}\}', value)
            for var in vars_in_value:
                var_clean = var.strip()
                
                # Always remove clearly fake link variables
                if FAKE_PATTERNS.match(var_clean):
                    old = "{{" + var + "}}"
                    # Remove lines that are primarily about the fake link
                    lines = value.split("\\n")
                    new_lines = []
                    for l in lines:
                        if old in l:
                            # Remove the fake variable
                            cleaned = l.replace(old, "").strip()
                            # If the line still has meaningful content, keep it
                            if cleaned and not cleaned.rstrip(".:!?, ") == "":
                                # Check if it's just a link intro ("Please use this link:", "Click here:")
                                link_intros = ["link", "click", "confirm", "use this", "booking", "schedule"]
                                is_link_intro = any(kw in cleaned.lower() for kw in link_intros) and len(cleaned) < 80
                                if not is_link_intro:
                                    new_lines.append(cleaned)
                        else:
                            new_lines.append(l)
                    params[key] = "\\n".join(new_lines)
                    value = params[key]
                    modified = True
                    print(f"[AI Generator] Removed fake variable {{{{{var_clean}}}}} from node {node.get('label', nid)}")
                    continue
                
                # If upstream has AI nodes, those can produce any variable — skip validation
                if upstream_has_ai:
                    continue
                
                # Check if variable is known
                if var_clean not in available:
                    # Unknown variable with no AI upstream — remove it
                    old = "{{" + var + "}}"
                    params[key] = value.replace(old, "")
                    value = params[key]
                    modified = True
                    print(f"[AI Generator] Removed unknown variable {{{{{var_clean}}}}} from node {node.get('label', nid)} (not produced by any upstream node)")
    
    if modified:
        # Clean up empty lines from removals
        for node in nodes:
            params = node.get("parameters", {})
            for key, value in params.items():
                if isinstance(value, str):
                    # Remove double newlines and trailing whitespace
                    while "\\n\\n\\n" in value:
                        value = value.replace("\\n\\n\\n", "\\n\\n")
                    params[key] = value.strip()
    
    return nodes


def apply_approval_defaults(nodes: list) -> list:
    """Apply requiresApproval defaults to nodes that don't have it explicitly set."""
    for node in nodes:
        node_type = node.get("type", "")
        if "requiresApproval" not in node:
            if node_type in APPROVAL_DEFAULT_NODES:
                node["requiresApproval"] = True
            elif node_type in NO_APPROVAL_NODES:
                node["requiresApproval"] = False
            # else: leave unset (unknown types default to False in runner)
    return nodes


def _generate_with_openai(prompt: str, connected_providers: list[str] = None) -> dict:
    """Use OpenAI to generate workflow"""
    try:
        import openai
        
        client = openai.OpenAI(api_key=settings.openai_api_key)

        # Build dynamic connection context
        connection_context = ""
        if connected_providers:
            connected_str = ", ".join(connected_providers)
            connection_context = (
                "\n\nUSER'S CONNECTED SERVICES: " + connected_str +
                "\n- Only use node types for services the user has connected."
                "\n- If the workflow requires a service not in the list above, still include it but add a note in the workflow summary.\n"
            )
        
        system_prompt = """You are a workflow automation assistant for Aivaro, a tool that helps non-technical founders automate their business processes.

Generate a workflow based on the user's description. Return a JSON object with:
- workflowName: A short, descriptive name (3-5 words)
- summary: A plain English sentence starting with "When... Aivaro will..."
- nodes: Array of nodes with {id, type, label, position: {x, y}, parameters, requiresApproval}
- edges: Array of edges with {id, source, target}
""" + connection_context + """Available TRIGGER node types (must be first node):
- start_manual: Manual start trigger (when user clicks "Run")
- start_form: Form submission trigger (when someone fills a form)
- start_schedule: Scheduled trigger (runs on a schedule). Parameters: {time: "09:00", frequency: "daily/weekly/monthly"}
- start_email: Email received trigger - monitors the user's CONNECTED Gmail account for new emails matching criteria. Use this when user says "when I receive an email", "when an email comes in", "when I get an email", etc. Parameters: {subject: "keyword to match", from: "optional@sender.com"}

IMPORTANT: When the user mentions receiving emails, getting emails, or email triggers, they mean their connected Gmail account. The start_email trigger monitors their Gmail inbox automatically.

Available ACTION node types:
- send_email: Send an email. Parameters: {to: "{{sender_email}}", subject: "Re: {{subject}}", body: "..."}
- ai_reply: Generate an AI response to an email. IMPORTANT: This only GENERATES a reply — it does NOT send it. You MUST add a send_email step after ai_reply to actually deliver the response. Parameters: {context: "...", tone: "professional/friendly/casual"}. Output: {{ai_response}}
- ai_summarize: Use AI to summarize data. Parameters: {source: "...", format: "bullet_points/paragraph"}
- append_row: Add row to Google Sheets. Parameters: {spreadsheet: "...", sheet_name: "Sheet1", columns: [{name: "...", value: "{{...}}"}]}
- read_sheet: Read data from Google Sheets. Parameters: {spreadsheet_id: "spreadsheet ID or file name (e.g. 'Contacts.xlsx')", spreadsheet_name: "optional display name", range: "Sheet1!A1:Z1000"}. Output: rows (array of {header_name: value} dicts), headers, row_count. IMPORTANT: read_sheet automatically triggers FOR-EACH iteration — all downstream nodes execute ONCE PER ROW with each row's fields available as {{column_name}} variables (headers lowercased, spaces become underscores). You do NOT need a loop node.
- delay: Wait for a duration. Parameters: {duration: 2, unit: "hours/minutes/days"}
- send_notification: Log an internal note to the workflow execution log. Parameters: {message: "..."}. NOTE: This does NOT send any message to anyone — it only records a note in the execution log visible in the dashboard. To actually notify the workflow owner, use send_email (to={{user_email}}), slack_send_dm (email={{user_email}}), or twilio_send_sms. NEVER use send_notification as a substitute for real owner notifications.
- email_template: Render a deterministic email template with variable substitution. NO AI involved — just fills in {{variables}}. Use this instead of ai_reply when you know exactly what the email should say (reminders, notifications, confirmations, etc.). Parameters: {to: "{{email}}", subject: "Reminder: ...", body: "Hi {{name}},\\n\\nThis is a reminder..."} Output: template_to, template_subject, template_body. Follow with send_email using {{template_to}}, {{template_subject}}, {{template_body}}.
- send_slack: Send a Slack message to a CHANNEL. Parameters: {channel: "#general", message: "..."}. Only use for posting to channels.
- slack_send_dm: Send a direct message to a specific PERSON on Slack. Parameters: {email: "user@email.com", message: "..."}. Use this when the user wants to message a specific person (NOT a channel).
- http_request: Make an API call. Parameters: {url: "...", method: "GET/POST"}
- condition: Branch the workflow based on a condition. Parameters: {field: "calendly_count", operator: "greater_than", value: "0"}. Operators: equals, not_equals, contains, greater_than, less_than, is_empty, is_not_empty. IMPORTANT: Condition nodes create TWO branches. Edges from condition nodes MUST have sourceHandle: "yes" (condition met/true) or sourceHandle: "no" (condition not met/false). NEVER use "true"/"false" as sourceHandle values — ONLY "yes" and "no". Each branch leads to different next steps.

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
1. For booking/appointment workflows → ALWAYS start with ai_reply to EXTRACT the requested date, time, customer name, and customer email from the email body. Then use google_calendar_create to book it. Do NOT use calendly_create_link unless the user specifically asks for a Calendly scheduling link.
2. For payment reminders → use delay + stripe_check_payment + condition
3. When user says "when I receive an email", "when I get an email", "when an email comes in", "emails from X", etc. → ALWAYS use start_email trigger. This monitors their connected Gmail inbox.
4. For auto-reply workflows → use ai_reply node to generate smart responses, then ALWAYS follow with a send_email node to actually send the reply. ai_reply generates the text, send_email delivers it. Never create an email reply workflow without a send_email step.
5. COMPLETE EMAIL REPLY PATTERN: start_email → ai_reply → send_email (to={{sender_email}}, subject="Re: {{subject}}", body="{{ai_response}}").
6. For Stripe invoices with auto_send=false → MUST add a stripe_send_invoice step after stripe_create_invoice.
7. For Stripe invoices with auto_send=true → no additional send step needed, but tell the user the invoice will be auto-sent.
8. mailchimp_send_campaign creates AND immediately sends — this is irreversible. ALWAYS set requiresApproval=true on this node.
9. twilio_make_call uses text-to-speech (robotic voice). Note this in the step label or description.
10. PLACEHOLDER VALUES: When using Airtable (base_id: "appXXX"), Notion (database_id), Calendly (event_type_uuid), or Mailchimp (list_id) — these are placeholders. The user MUST fill them in from their actual account. Flag these clearly.
11. For CRM/database workflows → prefer airtable_create_record or notion_create_page for storing customer data
12. For marketing/newsletter workflows → use mailchimp_add_subscriber to add contacts
13. For SMS notifications → use twilio_send_sms for text confirmations
14. For booking/appointment scheduling → use google_calendar_create (NOT calendly_create_link which requires paid Calendly plan)
15. Available template variables: {{sender_email}}, {{sender_name}}, {{from}}, {{to}}, {{subject}}, {{snippet}}, {{body}}, {{email}}, {{name}}, {{date}}, {{time}}, {{amount}}, {{payment_link_url}}, {{phone}}, {{ai_response}}, {{user_email}}
16. Always connect nodes with edges
17. Position nodes vertically, starting at y=50, spaced 150px apart, x=250
18. Default requiresApproval: true for: emails to external recipients, payment processing, campaign sends, phone calls. BUT if the user explicitly said "no approval", "auto-send", "don't ask me", or similar → set requiresApproval: false on ALL nodes. The user's explicit preference ALWAYS overrides the default.
19. The start_email trigger monitors the user's connected Gmail account - do NOT ask them to set up webhooks or external services
20. Only use node types listed in this prompt (hardcoded types above + any MCP integration types listed below). If a user requests a service not available, explain what services ARE available and suggest the closest alternative.
21. CONDITION BRANCHING: When using condition nodes, create TWO separate paths with edges that have sourceHandle="yes" and sourceHandle="no". The true branch runs when the condition is met, false when not met. Example: condition checks "calendly_count greater_than 0" → true branch = conflict exists (deny), false branch = no conflict (proceed). NEVER run both branches sequentially.

IMPORTANT — CONDITION NODES CAN ONLY DO SIMPLE FIELD COMPARISONS:
The condition node checks: input_data[field] <operator> value. Available operators: equals, not_equals, contains, greater_than, less_than, is_empty, is_not_empty.
- The "field" MUST be a key that a previous node's output actually produces.
- For AI extraction steps (ai_reply with extract mode), the output keys are whatever the AI returns — typically: is_appointment (true/false), customer_name, customer_email, requested_date, requested_time, etc.
- When checking boolean AI outputs, use: field="is_appointment", operator="equals", value="true" (string comparison — AI outputs are always strings).
- When checking list counts, use: field="calendly_count", operator="greater_than", value="0".
- DO NOT create conditions that check fields no previous node produces.
- If you need complex logic (e.g., "is this email about an appointment?"), use an ai_reply node first that outputs a clear field like "is_appointment": "true", then condition on that field.
- The "contains" operator checks if VALUE is contained in FIELD — e.g., field="subject", operator="contains", value="appointment" checks if the subject contains "appointment".
22. SLACK DMs vs CHANNELS: When the user wants to message a specific person on Slack, use slack_send_dm (NOT send_slack). send_slack is ONLY for posting to channels like #general. slack_send_dm takes an email parameter to find the user.
23. When the user asks to "notify" or "message" a specific person on Slack, use slack_send_dm with that person's email (or ask for their email if not provided).
24. NEVER HARDCODE emails, names, URLs, or IDs in workflow parameters. NEVER use placeholder strings like "ABEL_YAGUBYAN_EMAIL_PLACEHOLDER" or "DEFAULT_EVENT_TYPE_UUID_PLACEHOLDER". ALWAYS use {{variable}} references instead:
   - Workflow owner's email: {{user_email}}
   - Workflow owner's name: {{name}}
   - Customer/sender email: {{sender_email}} or {{from}}
   - Customer name: {{sender_name}} or {{customer_name}}
   The system automatically provides user_email and name from the authenticated user's profile at runtime.
25. NEVER use http_request as a substitute for built-in integrations. If we have a node type for it (calendly_list_events, google_calendar_list, etc.), use that — NOT http_request with a made-up URL. http_request is ONLY for external APIs we don't have built-in support for.
26. When using ai_reply for field extraction, the AI MUST output a JSON object with fields that downstream condition nodes check. The context param MUST explicitly list the required output fields. Example context: "Extract these fields as JSON: sender_email, requested_date, requested_time, is_appointment (true/false)."
27. The send_email node's "to" parameter should use {{sender_email}} to reply to the original sender. This is the parsed email address from the From header. {{from}} contains the full "Name <email>" string which may not work as a recipient. Available email trigger variables: {{sender_email}}, {{sender_name}}, {{from}}, {{subject}}, {{snippet}}, {{body}}, {{user_email}} (workflow owner).
28. APPOINTMENT/BOOKING WORKFLOW PATTERN: start_email -> ai_reply (extract is_appointment, customer_name, customer_email, requested_date, requested_time) -> condition (is_appointment equals true) -> google_calendar_create (using extracted date/time) -> send_email confirmation. The ai_reply extraction step is CRITICAL -- without it, you have no structured data. NEVER skip it.
29. When using calendly_list_events to check for conflicts, FILTER by the requested date using min_start_time and max_start_time parameters. Do NOT list ALL events -- that checks the wrong thing.
30. NON-MATCHING CONDITION BRANCHES: When the "no" branch of a condition means "this email is irrelevant" (e.g., not an appointment), do NOT send any email or notification. Just let the workflow end silently. Only create a "no" branch action when the user explicitly asks for one (e.g., "send a rejection email"). Ignoring irrelevant emails is the correct default behavior.
31. NEVER reference {{calendly_event_link}}, {{calendly_link}}, {{booking_link}}, or any link variable unless a previous workflow step actually CREATES that link. google_calendar_create does NOT produce a link. If you need to send a confirmation, just confirm the date/time — do NOT include a fake link variable.
32. SERVICE DISAMBIGUATION: When the user's request could be fulfilled by MULTIPLE connected services (e.g., sending email via Gmail send_email vs Brevo brevo_send_transactional_email vs SendGrid sendgrid_send_email), use the SPECIFIC service they mentioned. If they didn't specify, prefer the service that best fits the use case:
   - Transactional/bulk email to customers → Brevo or SendGrid (if connected)
   - Personal email replies → Gmail (send_email)
   - Marketing campaigns → Mailchimp or Brevo campaigns
   - SMS → Twilio or Brevo SMS (whichever is connected)
   If ambiguous AND multiple services are connected, note in the summary which service is being used and why.
33. FOR-EACH ITERATION: When read_sheet is followed by action nodes (send_email, brevo_send_transactional_email, etc.), the runner automatically executes downstream nodes ONCE PER ROW. Each row's column values are available as {{column_name}} (lowercased, spaces→underscores). Example: sheet headers ["Name", "Email", "Phone"] → {{name}}, {{email}}, {{phone}}. You do NOT need to reference sheet_data or build loops.
34. USE email_template INSTEAD OF ai_reply for deterministic emails (reminders, notifications, confirmations, invoices). ai_reply is ONLY for when you need the AI to compose content dynamically (e.g., "respond to this email intelligently"). If the user specifies what the email should say, use email_template → send_email (with {{template_to}}, {{template_subject}}, {{template_body}}). This is faster, cheaper, and deterministic.
35. SHEET-TO-EMAIL PATTERN: read_sheet → email_template → send_email. The template renders per-row, and send_email sends per-row. The email_template output fields are template_to, template_subject, template_body — use these in the send_email parameters. For Brevo: read_sheet → email_template → brevo_send_transactional_email (with to_email={{template_to}}, subject={{template_subject}}, text_content={{template_body}}, sender_email={{my_email}}).
36. ALWAYS fill MCP node parameters with {{variable}} references when data comes from previous nodes. NEVER leave parameters empty. If read_sheet has columns Name and Email, use to_email="{{email}}", subject="Reminder for {{name}}", etc.

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

Example for condition branching (appointment with conflict check):
{
  "workflowName": "Appointment Workflow",
  "summary": "When an appointment email arrives, extract the requested date/time, create a calendar event and confirm. Non-appointment emails are ignored.",
  "nodes": [
    {"id": "1", "type": "start_email", "label": "When appointment email received", "position": {"x": 250, "y": 50}, "parameters": {}},
    {"id": "2", "type": "ai_reply", "label": "Extract appointment details", "position": {"x": 250, "y": 200}, "parameters": {"prompt": "Extract the following from this email in JSON format: {\"is_appointment\": true/false, \"customer_name\": \"...\", \"customer_email\": \"...\", \"requested_date\": \"YYYY-MM-DD\", \"requested_time\": \"HH:MM\", \"service_type\": \"...\"}. Email from {{name}} ({{sender_email}}): Subject: {{subject}} Body: {{snippet}}", "context": "You are an email parser. Extract appointment details. If the email is not about an appointment, set is_appointment to false."}},
    {"id": "3", "type": "condition", "label": "Is this about an appointment?", "position": {"x": 250, "y": 350}, "parameters": {"field": "is_appointment", "operator": "equals", "value": "true"}},
    {"id": "4", "type": "google_calendar_create", "label": "Create calendar event", "position": {"x": 250, "y": 500}, "parameters": {"title": "Appointment with {{customer_name}}", "date": "{{requested_date}}", "time": "{{requested_time}}", "duration": 60, "description": "Service: {{service_type}}. Customer: {{customer_name}} ({{customer_email}})"}},
    {"id": "5", "type": "send_email", "label": "Send confirmation email", "position": {"x": 250, "y": 650}, "parameters": {"to": "{{sender_email}}", "subject": "Re: {{subject}}", "body": "Hi {{customer_name}},\\n\\nYour appointment on {{requested_date}} at {{requested_time}} has been confirmed.\\n\\nThank you!"}, "requiresApproval": true}
  ],
  "edges": [
    {"id": "e1", "source": "1", "target": "2"},
    {"id": "e2", "source": "2", "target": "3"},
    {"id": "e4", "source": "3", "target": "4", "sourceHandle": "yes", "label": "is appointment"},
    {"id": "e5", "source": "4", "target": "5"}
  ]
}

Example for sheet-to-email (for-each pattern):
{
  "workflowName": "Weekly Payment Reminders",
  "summary": "Every Tuesday at 2 PM, Aivaro will read contacts from Google Sheets and send each person a payment reminder email.",
  "nodes": [
    {"id": "1", "type": "start_schedule", "label": "Every Tuesday at 2 PM PT", "position": {"x": 250, "y": 50}, "parameters": {"time": "14:00", "frequency": "weekly"}},
    {"id": "2", "type": "read_sheet", "label": "Read contacts from Google Sheet", "position": {"x": 250, "y": 200}, "parameters": {"spreadsheet_id": "My Contacts", "range": "Sheet1!A1:C1000"}},
    {"id": "3", "type": "email_template", "label": "Compose reminder email", "position": {"x": 250, "y": 350}, "parameters": {"to": "{{email}}", "subject": "Payment Reminder", "body": "Hi {{name}},\n\nThis is a friendly reminder that your payment is due.\n\nPlease contact us at {{my_email}} if you have questions.\n\nThank you!"}},
    {"id": "4", "type": "send_email", "label": "Send reminder email", "position": {"x": 250, "y": 500}, "parameters": {"to": "{{template_to}}", "subject": "{{template_subject}}", "body": "{{template_body}}"}, "requiresApproval": true}
  ],
  "edges": [
    {"id": "e1", "source": "1", "target": "2"},
    {"id": "e2", "source": "2", "target": "3"},
    {"id": "e3", "source": "3", "target": "4"}
  ]
}

Return ONLY valid JSON, no markdown code blocks or explanation."""

        # Inject MCP tool documentation for non-hardcoded providers
        mcp_docs = _get_mcp_tool_docs(connected_providers)
        if mcp_docs:
            system_prompt += mcp_docs

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a workflow for: {prompt}"}
            ],
            max_completion_tokens=16384
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
                    "to": "{{sender_email}}",
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
