from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.models import Workflow, Execution, ExecutionNode, Approval, Connection
from app.services.node_executor import execute_node


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
    
    def get_next_nodes(self, node_id: str) -> list[str]:
        """Get node IDs connected from this node"""
        return [e["target"] for e in self.edges if e["source"] == node_id]
    
    def run(self, trigger_data: Optional[dict] = None) -> Execution:
        """Execute the workflow"""
        try:
            start_nodes = self.get_start_nodes()
            
            if not start_nodes:
                print(f"[WorkflowRunner] No start nodes found in workflow {self.workflow.id}")
                self.execution.status = "failed"
                self.db.commit()
                return self.execution
            
            # Start with the first start node
            current_data = trigger_data or self._generate_mock_trigger_data()
            print(f"[WorkflowRunner] Starting execution from node {start_nodes[0]['id']} with data: {list(current_data.keys())}")
            self._execute_from_node(start_nodes[0]["id"], current_data)
            
            return self.execution
        except Exception as e:
            import traceback
            error_msg = f"Workflow execution failed: {str(e)}\n{traceback.format_exc()}"
            print(f"[WorkflowRunner] {error_msg}")
            self.execution.status = "failed"
            self.db.commit()
            return self.execution
        
        return self.execution
    
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
        if node.get("requiresApproval", False):
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
                is_test=self.execution.is_test,
                connections=self.connections
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
            self.db.commit()
            return
        
        # Continue to next nodes
        next_node_ids = self.get_next_nodes(node_id)
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
            recipient = params.get("to", input_data.get("email", "recipient"))
            recipient = self._interpolate(recipient, input_data)
            return f"Send an email to {recipient}"
        elif node_type == "append_row":
            sheet = params.get("spreadsheet", "your spreadsheet")
            return f"Add a row to {sheet}"
        else:
            return f"Execute {node.get('label', node_type)}"
    
    def _generate_action_details(self, node: dict, input_data: dict) -> dict:
        """Generate detailed preview of the action"""
        node_type = node["type"]
        params = node.get("parameters", {})
        
        if node_type == "send_email":
            to = self._interpolate(params.get("to", input_data.get("email", "")), input_data)
            subject = self._interpolate(params.get("subject", ""), input_data)
            body = self._interpolate(params.get("body", ""), input_data)
            return {
                "type": "email",
                "to": to,
                "subject": subject,
                "body_preview": body[:500] + ("..." if len(body) > 500 else "")
            }
        return {"type": node_type, "parameters": params}
    
    def _interpolate(self, template: str, data: dict) -> str:
        """Replace {{variable}} with values from data"""
        result = template
        for key, value in data.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    def _generate_mock_trigger_data(self) -> dict:
        """Generate initial data for manual runs - uses actual user info when available"""
        # Get the user's actual email from the workflow owner
        user_email = None
        user_name = None
        if self.workflow and self.workflow.user:
            user_email = self.workflow.user.email
            user_name = self.workflow.user.full_name or self.workflow.user.email.split('@')[0]
        
        return {
            "name": user_name or "User",
            "email": user_email or "user@example.com",
            "user_email": user_email or "user@example.com",
            "today": datetime.utcnow().strftime("%Y-%m-%d"),
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
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
            is_test=self.execution.is_test,
            connections=self.connections
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
        next_node_ids = self.get_next_nodes(approval.node_id)
        if not next_node_ids:
            self.execution.status = "completed"
            self.execution.completed_at = datetime.utcnow()
            self.db.commit()
            return
        
        for next_id in next_node_ids:
            self._execute_from_node(next_id, result.get("output", {}))
