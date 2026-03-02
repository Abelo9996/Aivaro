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
        self.connections = self._load_connections()
    
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
        If no edges match the branch filter, fall back to all edges (backward compat).
        """
        if branch:
            # Try to find edges with matching sourceHandle
            branched = [e["target"] for e in self.edges 
                       if e["source"] == node_id and e.get("sourceHandle") == branch]
            if branched:
                return branched
            # Also try label-based matching
            branched = [e["target"] for e in self.edges 
                       if e["source"] == node_id and e.get("label", "").lower() == branch]
            if branched:
                return branched
        return [e["target"] for e in self.edges if e["source"] == node_id]
    
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
                increment_run_count(user, self.db)

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
        if self.workflow and self.workflow.user:
            user_email = self.workflow.user.email
            user_name = self.workflow.user.full_name or self.workflow.user.email.split('@')[0]
        
        # Get timezone-aware current time (Pacific Time by default)
        local_now = now_local()
        
        # Base data always includes user info and timestamps (in Pacific Time)
        base_data = {
            "name": user_name or "User",
            "email": user_email or "user@example.com",
            "user_email": user_email or "user@example.com",
            "today": local_now.strftime("%Y-%m-%d"),
            "date": local_now.strftime("%Y-%m-%d"),
            "current_time": local_now.strftime("%H:%M"),
            "timestamp": local_now.isoformat(),
            "timezone": "America/Los_Angeles",
        }
        
        # If we have real trigger data, merge it (trigger data takes precedence)
        if trigger_data and len(trigger_data) > 0:
            print(f"[WorkflowRunner] Using REAL trigger data with keys: {list(trigger_data.keys())}")
            print(f"[WorkflowRunner] Trigger data snippet: {trigger_data.get('snippet', 'N/A')[:100] if trigger_data.get('snippet') else 'No snippet'}")
            # Real trigger data - use it, with base data as fallback
            return {**base_data, **trigger_data}
        
        # No trigger data - manual run without real trigger data
        # Use base data only, no mock/demo data
        is_manual = self.execution.trigger_data is None or len(self.execution.trigger_data or {}) == 0
        
        if is_manual:
            print(f"[WorkflowRunner] MANUAL RUN - no trigger data available, using base user data only")
            return base_data
        else:
            return base_data
    
    def _execute_from_node(self, node_id: str, input_data: dict):
        """Execute starting from a specific node"""
        node = self.nodes.get(node_id)
        if not node:
            print(f"[WorkflowRunner] Node not found: {node_id}")
            return
        
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
            self._create_approval(node, exec_node, input_data)
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
            self.execution.error = f"Node '{node.get('label', node_id)}' failed: {result.get('logs', 'Unknown error')}"
            self.db.commit()
            return
        
        # Continue to next nodes (with branch support for conditions)
        branch = result.get("branch")
        next_node_ids = self.get_next_nodes(node_id, branch=branch)
        if not next_node_ids:
            self.execution.status = "completed"
            self.execution.completed_at = datetime.utcnow()
            self.db.commit()
            return
        
        for next_id in next_node_ids:
            self._execute_from_node(next_id, result.get("output", {}))
    
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
