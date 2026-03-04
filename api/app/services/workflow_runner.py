from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.models import Workflow, Execution, ExecutionNode, Approval, Connection, User
from app.services.node_executor import execute_node
from app.utils.timezone import now_local, now_utc, today_local, current_time_local


class WorkflowRunner:
    def __init__(self, db: Session, execution_id: UUID):
        self.db = db
        self.execution = db.query(Execution).filter(Execution.id == execution_id).first()
        self.workflow = self.execution.workflow
        self.nodes = {n["id"]: n for n in self.workflow.nodes}
        self.edges = self.workflow.edges
        self._fix_condition_edges()  # Repair missing sourceHandle on condition edges
        self.connections = self._load_connections()
    
    def _fix_condition_edges(self):
        """Auto-repair edges from condition nodes that are missing sourceHandle.
        
        If a condition node has exactly 2 outgoing edges with no sourceHandle,
        assign 'yes' to the first and 'no' to the second. This fixes workflows
        created before the fix_condition_edges post-processor existed.
        """
        condition_ids = {nid for nid, n in self.nodes.items() if n.get("type") == "condition"}
        if not condition_ids:
            return
        
        for cid in condition_ids:
            outgoing = [e for e in self.edges if e.get("source") == cid]
            has_handles = any(e.get("sourceHandle") for e in outgoing)
            if has_handles:
                continue  # Already has sourceHandle, skip
            
            if len(outgoing) == 2:
                # Assign yes/no based on position or order
                # Try to match by target node labels if possible
                for e in outgoing:
                    target_node = self.nodes.get(e.get("target", ""), {})
                    label = target_node.get("label", "").lower()
                    # Heuristic: if label contains rejection/conflict/not/decline → "no" branch
                    if any(kw in label for kw in ["reject", "conflict", "not ", "decline", "cancel", "fail", "no"]):
                        e["sourceHandle"] = "no"
                    elif any(kw in label for kw in ["confirm", "accept", "create", "book", "schedule", "yes", "send confirm"]):
                        e["sourceHandle"] = "yes"
                
                # If heuristics didn't assign both, use order: first=yes, second=no
                assigned = [e.get("sourceHandle") for e in outgoing]
                if assigned[0] and not assigned[1]:
                    outgoing[1]["sourceHandle"] = "no" if assigned[0] == "yes" else "yes"
                elif assigned[1] and not assigned[0]:
                    outgoing[0]["sourceHandle"] = "no" if assigned[1] == "yes" else "yes"
                elif not assigned[0] and not assigned[1]:
                    outgoing[0]["sourceHandle"] = "yes"
                    outgoing[1]["sourceHandle"] = "no"
                
                print(f"[WorkflowRunner] Auto-fixed sourceHandle on condition node {cid}: {[(e.get('sourceHandle'), self.nodes.get(e.get('target','')).get('label','?')) for e in outgoing]}")
            elif len(outgoing) == 1:
                # Single edge from condition — always follow it regardless of branch
                outgoing[0]["sourceHandle"] = "yes"
                # Also add a synthetic "no" handle so it doesn't block
                print(f"[WorkflowRunner] Condition node {cid} has only 1 outgoing edge. Assigned sourceHandle='yes'.")

    def _load_connections(self) -> dict:
        """Load user's connections for use in node execution."""
        user_id = self.workflow.user_id
        connections_data = {}
        
        connections = self.db.query(Connection).filter(
            Connection.user_id == user_id,
            Connection.is_connected == True
        ).all()
        
        for conn in connections:
            if conn.credentials:
                connections_data[conn.type] = conn.credentials
        
        return connections_data
        
    def get_start_nodes(self) -> list[dict]:
        """Find nodes with type 'start'"""
        return [n for n in self.workflow.nodes if n["type"].startswith("start")]
    
    def get_next_nodes(self, node_id: str, branch: str = None) -> list[str]:
        """Get node IDs connected from this node, optionally filtered by branch.
        
        For condition nodes, edges should have sourceHandle='yes' or sourceHandle='no'.
        If branch is specified, only return edges matching that branch.
        If no edges match, return EMPTY (do NOT fall back to all edges).
        """
        all_edges = [e for e in self.edges if e["source"] == node_id]
        
        if branch:
            # Normalize: yes/true both match, no/false both match
            BRANCH_ALIASES = {
                "yes": {"yes", "true", "Yes", "True"},
                "no": {"no", "false", "No", "False"},
            }
            match_set = BRANCH_ALIASES.get(branch, {branch})
            
            # Try sourceHandle match (with aliases)
            branched = [e["target"] for e in all_edges if e.get("sourceHandle") in match_set]
            if branched:
                print(f"[WorkflowRunner] Node {node_id} branch='{branch}' → {len(branched)} targets via sourceHandle")
                return branched
            
            # Try label match (with aliases)
            branched = [e["target"] for e in all_edges if e.get("label", "").lower() in {s.lower() for s in match_set}]
            if branched:
                print(f"[WorkflowRunner] Node {node_id} branch='{branch}' → {len(branched)} targets via label")
                return branched
            
            # No matching branch edges found
            # Check if ANY edges from this node have sourceHandle set
            has_any_handles = any(e.get("sourceHandle") for e in all_edges)
            if not has_any_handles:
                # No sourceHandles — check if this is a condition node
                # For condition nodes, missing sourceHandles is a workflow definition bug
                # Try label-based matching first, then stop (don't run both branches)
                node_def = self.nodes.get(node_id)
                node_type = node_def.get("type", "") if node_def else ""
                if node_type == "condition":
                    print(f"[WorkflowRunner] WARNING: Condition node {node_id} has NO sourceHandle on edges. Branch='{branch}'. Stopping to prevent running both branches. Fix: add sourceHandle='yes'/'no' to edges from this condition.")
                    return []
                # Non-condition node — treat as linear flow
                print(f"[WorkflowRunner] Node {node_id} branch='{branch}' but NO edges have sourceHandle. Treating as linear flow → {len(all_edges)} targets.")
                return [e["target"] for e in all_edges]
            
            # Some edges have handles but none matched this branch — stop this path
            edge_handles = [(e.get("sourceHandle"), e.get("label")) for e in all_edges]
            print(f"[WorkflowRunner] WARNING: Node {node_id} branch='{branch}' matched NO edges. Available: {edge_handles}. Stopping this path.")
            return []
        
        return [e["target"] for e in all_edges]
    
    def run(self, trigger_data: Optional[dict] = None) -> Execution:
        """Execute the workflow"""
        try:
            # Enforce plan limits
            from app.services.plan_limits import check_can_run_workflow, increment_run_count
            user = self.db.query(User).filter(User.id == self.workflow.user_id).first()
            if user:
                try:
                    check_can_run_workflow(user)
                except Exception as limit_err:
                    self.execution.status = "failed"
                    self.execution.error = str(getattr(limit_err, 'detail', {}).get('message', 'Plan limit reached'))
                    self.db.commit()
                    return self.execution

            start_nodes = self.get_start_nodes()
            
            if not start_nodes:
                print(f"[WorkflowRunner] No start nodes found in workflow {self.workflow.id}")
                self.execution.status = "failed"
                self.db.commit()
                return self.execution
            
            # Build the current data - merge base data with trigger data
            current_data = self._build_input_data(trigger_data)
            
            # Inject knowledge base context for AI nodes
            from app.services.knowledge_service import get_knowledge_context
            knowledge_ctx = get_knowledge_context(self.workflow.user_id, self.db)
            if knowledge_ctx:
                current_data["__knowledge_context"] = knowledge_ctx
            
            print(f"[WorkflowRunner] Starting execution from node {start_nodes[0]['id']} with data keys: {list(current_data.keys())}")
            print(f"[WorkflowRunner] Has real trigger data: {trigger_data is not None and len(trigger_data) > 0}")
            self._execute_from_node(start_nodes[0]["id"], current_data)
            
            # Only count successful/completed runs against the trial limit
            if user and self.execution.status in ("completed", "paused"):
                increment_run_count(user, self.db)
            
            return self.execution
        except Exception as e:
            import traceback
            error_msg = f"Workflow execution failed: {str(e)}\n{traceback.format_exc()}"
            print(f"[WorkflowRunner] {error_msg}")
            self.execution.status = "failed"
            self.execution.error = error_msg
            self.db.commit()
            return self.execution
        
        return self.execution
    
    def _build_input_data(self, trigger_data: Optional[dict] = None) -> dict:
        """Build input data by merging base user data with trigger data."""
        # Get the user's actual info
        user_email = None
        user_name = None
        owner_gmail = None
        if self.workflow and self.workflow.user:
            user_email = self.workflow.user.email
            user_name = self.workflow.user.full_name or self.workflow.user.email.split('@')[0]
            
            # Get the connected Google email (the actual Gmail they authenticated with)
            try:
                from app.models.connection import Connection
                import json
                google_conn = self.db.query(Connection).filter(
                    Connection.user_id == self.workflow.user_id,
                    Connection.type == "google"
                ).first()
                if google_conn:
                    creds = google_conn.credentials
                    if isinstance(creds, str):
                        creds = json.loads(creds)
                    # Email might be in user_info (from OAuth) or top-level
                    user_info = creds.get("user_info") or {}
                    owner_gmail = user_info.get("email") or creds.get("email") or creds.get("user_email")
            except Exception as e:
                print(f"[WorkflowRunner] Could not get Google email: {e}")
        
        # Get timezone-aware current time (Pacific Time by default)
        local_now = now_local()
        
        # Use connected Gmail as primary email if available
        effective_email = owner_gmail or user_email or "user@example.com"
        
        # Base data always includes user info and timestamps (in Pacific Time)
        base_data = {
            "name": user_name or "User",
            "email": effective_email,
            "user_email": effective_email,
            "owner_email": effective_email,
            "my_email": effective_email,
            "today": local_now.strftime("%Y-%m-%d"),
            "date": local_now.strftime("%Y-%m-%d"),
            "current_time": local_now.strftime("%H:%M"),
            "timestamp": local_now.isoformat(),
            "timezone": "America/Los_Angeles",
        }
        
        # If we have real trigger data, merge it
        # IMPORTANT: Protect owner fields from being overwritten by sender data
        if trigger_data and len(trigger_data) > 0:
            print(f"[WorkflowRunner] Using REAL trigger data with keys: {list(trigger_data.keys())}")
            merged = {**base_data, **trigger_data}
            # Restore owner fields that sender data may have overwritten
            merged["owner_email"] = base_data["owner_email"]
            merged["my_email"] = base_data["my_email"]
            merged["user_email"] = base_data["user_email"]
            return merged
        
        # Fallback: check execution's stored trigger_data (set when execution was created)
        stored = self.execution.trigger_data if self.execution else None
        if stored and len(stored) > 0:
            print(f"[WorkflowRunner] Using STORED trigger data with keys: {list(stored.keys())}")
            merged = {**base_data, **stored}
            merged["owner_email"] = base_data["owner_email"]
            merged["my_email"] = base_data["my_email"]
            merged["user_email"] = base_data["user_email"]
            return merged
        
        # No trigger data at all - manual run
        print(f"[WorkflowRunner] MANUAL RUN - no trigger data available, using base user data only")
        return base_data
    
    def _execute_from_node(self, node_id: str, input_data: dict):
        """Execute starting from a specific node"""
        node = self.nodes.get(node_id)
        if not node:
            print(f"[WorkflowRunner] Node not found: {node_id}")
            return
        
        print(f"[WorkflowRunner] _execute_from_node: {node.get('label', node_id)} (type={node['type']}) exec_status={self.execution.status}")
        
        # Create execution node record
        exec_node = ExecutionNode(
            execution_id=self.execution.id,
            node_id=node_id,
            node_type=node["type"],
            node_label=node.get("label"),
            status="running",
            input_data=input_data,
            started_at=datetime.utcnow()
        )
        self.db.add(exec_node)
        self.db.commit()
        
        self.execution.current_node_id = node_id
        self.db.commit()
        
        # Check if approval is required
        # The 'approval' node type ALWAYS requires approval
        if node.get("requiresApproval", False) or node["type"] == "approval":
            # Run the full 4-pass param resolution so approval shows complete values
            from app.services.node_executor import (
                _interpolate_params, _resolve_aliases_in_params,
                _clean_unresolved_variables, _autofill_empty_params
            )
            resolved_params = _interpolate_params(node.get("parameters", {}), input_data)
            resolved_params = _resolve_aliases_in_params(resolved_params, input_data)
            resolved_params = _clean_unresolved_variables(resolved_params)
            resolved_params = _autofill_empty_params(resolved_params, input_data)
            resolved_node = {**node, "parameters": resolved_params}
            self._create_approval(resolved_node, exec_node, input_data)
            exec_node.status = "waiting_approval"
            self.execution.status = "paused"
            self.db.commit()
            return
        
        # Execute the node with error handling
        try:
            result = execute_node(
                node_type=node["type"],
                parameters=node.get("parameters", {}),
                input_data=input_data,
                connections=self.connections,
                user_id=str(self.workflow.user_id),
                db=self.db,
            )
        except Exception as e:
            import traceback
            error_msg = f"Exception executing node {node_id} ({node['type']}): {str(e)}\n{traceback.format_exc()}"
            print(f"[WorkflowRunner] {error_msg}")
            exec_node.logs = error_msg
            exec_node.status = "failed"
            exec_node.completed_at = datetime.utcnow()
            exec_node.duration_ms = int((exec_node.completed_at - exec_node.started_at).total_seconds() * 1000)
            self.execution.status = "failed"
            self.execution.error = f"Node '{node.get('label', node_id)}' failed: {str(e)}"
            self.db.commit()
            return
        
        exec_node.output_data = result.get("output", {})
        exec_node.logs = result.get("logs", "")
        exec_node.status = "completed" if result.get("success") else "failed"
        exec_node.completed_at = datetime.utcnow()
        exec_node.duration_ms = int((exec_node.completed_at - exec_node.started_at).total_seconds() * 1000)
        self.db.commit()
        
        if not result.get("success"):
            exec_node.logs = exec_node.logs or f"Node returned failure: {result}"
            self.execution.status = "failed"
            self.execution.error = f"Node '{node.get('label', node_id)}' failed: {result.get('error', 'Unknown error')}"
            self.db.commit()
            return
        
        # Continue to next nodes (with branch support for conditions)
        branch = result.get("branch")
        next_node_ids = self.get_next_nodes(node_id, branch=branch)
        if not next_node_ids:
            # Only mark completed if we're NOT inside a for-each iteration
            # (for-each manages completion itself after all rows finish)
            if not getattr(self, '_in_foreach', False):
                self.execution.status = "completed"
                self.execution.completed_at = datetime.utcnow()
                self.db.commit()
            return
        
        output = result.get("output", {})
        
        # === FOR-EACH ITERATION ===
        # If the node flagged __iterate_rows and produced rows, execute downstream
        # nodes once per row with row fields merged into the data context.
        if output.get("__iterate_rows") and output.get("rows"):
            rows = output["rows"]
            print(f"[WorkflowRunner] FOR-EACH: Iterating {len(rows)} rows through {len(next_node_ids)} downstream nodes")
            
            # Remove iteration flags from the base data to prevent re-iteration
            base_data = {k: v for k, v in output.items() if k not in ("__iterate_rows", "rows")}
            
            # Set flag so leaf nodes don't mark execution as completed mid-iteration
            self._in_foreach = True
            
            for row_idx, row in enumerate(rows):
                # Merge row fields into the data context — row fields take priority
                row_data = {**base_data, **row}
                row_data["__row_index"] = row_idx
                row_data["__row_number"] = row_idx + 1
                row_data["__total_rows"] = len(rows)
                
                print(f"[WorkflowRunner] FOR-EACH row {row_idx + 1}/{len(rows)}: keys={list(row.keys())}")
                
                for next_id in next_node_ids:
                    self._execute_from_node(next_id, row_data)
                    
                    # If any iteration failed, stop (approval pauses should NOT stop — we want
                    # all rows to create their approvals so user can review them all at once)
                    if self.execution.status == "failed":
                        print(f"[WorkflowRunner] FOR-EACH stopped at row {row_idx + 1} due to failure")
                        self._in_foreach = False
                        return
                    
                    # Reset status back to running if it was set to paused by an approval
                    # (we'll set final paused status after all rows are processed)
                    if self.execution.status == "paused":
                        self._foreach_has_pending_approvals = True
                        self.execution.status = "running"
                        self.db.commit()
            
            # All rows processed
            self._in_foreach = False
            has_approvals = getattr(self, '_foreach_has_pending_approvals', False)
            self._foreach_has_pending_approvals = False
            
            if has_approvals:
                self.execution.status = "paused"
                self.db.commit()
                print(f"[WorkflowRunner] FOR-EACH complete — paused for pending approvals")
                return
            self.execution.status = "completed"
            self.execution.completed_at = datetime.utcnow()
            self.db.commit()
            return
        
        # === NORMAL FLOW (no iteration) ===
        for next_id in next_node_ids:
            self._execute_from_node(next_id, output)
    
    def _create_approval(self, node: dict, exec_node: ExecutionNode, input_data: dict):
        """Create an approval request"""
        action_summary = self._generate_action_summary(node, input_data)
        action_details = self._generate_action_details(node, input_data)
        
        approval = Approval(
            execution_id=self.execution.id,
            node_id=node["id"],
            status="pending",
            action_summary=action_summary,
            action_details=action_details
        )
        self.db.add(approval)
        self.db.commit()
    
    def _generate_action_summary(self, node: dict, input_data: dict) -> str:
        """Generate a plain English summary of what will happen"""
        node_type = node["type"]
        params = node.get("parameters", {})
        
        if node_type == "send_email":
            recipient = self._interpolate(params.get("to", input_data.get("email", "recipient")), input_data)
            subject = self._interpolate(params.get("subject", ""), input_data)
            return f"Send email to {recipient}: \"{subject}\""
        elif node_type == "stripe_create_payment_link":
            amount = params.get("amount", "?")
            product = self._interpolate(params.get("product_name", "payment"), input_data)
            return f"Create ${amount} payment link for \"{product}\""
        elif node_type == "stripe_create_invoice":
            amount = self._interpolate(str(params.get("amount", "?")), input_data)
            customer = self._interpolate(params.get("customer_email", "customer"), input_data)
            auto_send = params.get("auto_send", "false")
            suffix = " (will auto-send to customer)" if auto_send == "true" else " (draft, not sent yet)"
            return f"Create ${amount} Stripe invoice for {customer}{suffix}"
        elif node_type == "stripe_send_invoice":
            return "Send Stripe invoice to customer"
        elif node_type == "twilio_send_sms":
            to = self._interpolate(params.get("to", "recipient"), input_data)
            body_preview = self._interpolate(params.get("body", ""), input_data)[:80]
            return f"Send SMS to {to}: \"{body_preview}\""
        elif node_type == "twilio_send_whatsapp":
            to = self._interpolate(params.get("to", "recipient"), input_data)
            return f"Send WhatsApp message to {to}"
        elif node_type == "twilio_make_call":
            to = self._interpolate(params.get("to", "recipient"), input_data)
            return f"Make automated phone call to {to}"
        elif node_type == "mailchimp_send_campaign":
            subject = self._interpolate(params.get("subject", "campaign"), input_data)
            return f"Send email campaign: \"{subject}\" (IRREVERSIBLE - sends to entire audience)"
        elif node_type == "append_row":
            sheet = params.get("spreadsheet", "your spreadsheet")
            return f"Add a row to \"{sheet}\""
        elif node_type == "google_calendar_create":
            title = self._interpolate(params.get("title", "event"), input_data)
            date = self._interpolate(params.get("date", ""), input_data)
            return f"Create calendar event: \"{title}\" on {date}"
        elif node_type == "airtable_create_record":
            table = params.get("table_name", "table")
            return f"Create record in Airtable table \"{table}\""
        elif node_type == "airtable_update_record":
            table = params.get("table_name", "table")
            return f"Update record in Airtable table \"{table}\""
        else:
            label = node.get("label", node_type)
            return f"Execute: {label}"
    
    def _generate_action_details(self, node: dict, input_data: dict) -> dict:
        """Generate detailed preview of the action with interpolated values"""
        node_type = node["type"]
        params = node.get("parameters", {})
        
        if node_type == "send_email":
            return {
                "type": "email",
                "to": self._interpolate(params.get("to", input_data.get("email", "")), input_data),
                "subject": self._interpolate(params.get("subject", ""), input_data),
                "body_preview": self._interpolate(params.get("body", ""), input_data)[:500],
            }
        elif node_type == "stripe_create_payment_link":
            return {
                "type": "payment_link",
                "amount": params.get("amount"),
                "product_name": self._interpolate(params.get("product_name", ""), input_data),
                "success_message": self._interpolate(params.get("success_message", ""), input_data),
            }
        elif node_type == "stripe_create_invoice":
            return {
                "type": "invoice",
                "customer_email": self._interpolate(params.get("customer_email", ""), input_data),
                "amount": self._interpolate(str(params.get("amount", "")), input_data),
                "description": self._interpolate(params.get("description", ""), input_data),
                "due_days": params.get("due_days"),
                "auto_send": params.get("auto_send", "false"),
            }
        elif node_type == "twilio_send_sms":
            return {
                "type": "sms",
                "to": self._interpolate(params.get("to", ""), input_data),
                "body": self._interpolate(params.get("body", ""), input_data),
            }
        elif node_type == "twilio_send_whatsapp":
            return {
                "type": "whatsapp",
                "to": self._interpolate(params.get("to", ""), input_data),
                "body": self._interpolate(params.get("body", ""), input_data),
                "media_url": params.get("media_url"),
            }
        elif node_type == "twilio_make_call":
            return {
                "type": "phone_call",
                "to": self._interpolate(params.get("to", ""), input_data),
                "message": self._interpolate(params.get("message", ""), input_data),
                "note": "Uses automated text-to-speech voice",
            }
        elif node_type == "mailchimp_send_campaign":
            return {
                "type": "email_campaign",
                "subject": self._interpolate(params.get("subject", ""), input_data),
                "from_name": params.get("from_name", ""),
                "warning": "This is irreversible. The campaign will be sent immediately to your entire audience.",
            }
        elif node_type == "google_calendar_create":
            return {
                "type": "calendar_event",
                "title": self._interpolate(params.get("title", ""), input_data),
                "date": self._interpolate(params.get("date", ""), input_data),
                "start_time": self._interpolate(params.get("start_time", ""), input_data),
                "duration_hours": params.get("duration"),
            }
        else:
            # Interpolate all string parameter values for generic fallback
            interpolated = {}
            for k, v in params.items():
                if isinstance(v, str):
                    interpolated[k] = self._interpolate(v, input_data)
                else:
                    interpolated[k] = v
            return {"type": node_type, "label": node.get("label", node_type), "parameters": interpolated}
    
    def _interpolate(self, template: str, data: dict) -> str:
        """Replace {{variable}} with values from data"""
        result = template
        for key, value in data.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    def resume_from_approval(self, approval_id: UUID):
        """Resume execution after approval"""
        approval = self.db.query(Approval).filter(Approval.id == approval_id).first()
        if not approval or approval.status != "approved":
            return
        
        node = self.nodes.get(approval.node_id)
        exec_node = self.db.query(ExecutionNode).filter(
            ExecutionNode.execution_id == self.execution.id,
            ExecutionNode.node_id == approval.node_id
        ).first()
        
        if not exec_node:
            return
        
        # Execute the approved node
        result = execute_node(
            node_type=node["type"],
            parameters=node.get("parameters", {}),
            input_data=exec_node.input_data,
            connections=self.connections,
            user_id=str(self.workflow.user_id),
            db=self.db,
        )
        
        exec_node.output_data = result.get("output", {})
        exec_node.logs = result.get("logs", "")
        exec_node.status = "completed" if result.get("success") else "failed"
        exec_node.completed_at = datetime.utcnow()
        exec_node.duration_ms = int((exec_node.completed_at - exec_node.started_at).total_seconds() * 1000)
        self.db.commit()
        
        self.execution.status = "running"
        self.db.commit()
        
        # Continue to next nodes
        branch = result.get("branch")
        next_node_ids = self.get_next_nodes(approval.node_id, branch=branch)
        if not next_node_ids:
            self.execution.status = "completed"
            self.execution.completed_at = datetime.utcnow()
            self.db.commit()
            return
        
        for next_id in next_node_ids:
            self._execute_from_node(next_id, result.get("output", {}))
