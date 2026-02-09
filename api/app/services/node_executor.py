"""
Node Executor - Executes individual workflow nodes using real integrations.
"""
from typing import Any, Optional
from datetime import datetime
import asyncio


class NodeExecutor:
    """Executes workflow nodes with real or mock integrations."""
    
    def __init__(self, connections: Optional[dict] = None):
        """
        Initialize with user's connections.
        connections should be a dict like:
        {
            "google": {"access_token": "...", "refresh_token": "..."},
            "slack": {"access_token": "..."},
        }
        """
        self.connections = connections or {}
        self._google_service = None
        self._slack_service = None
    
    async def get_google_service(self):
        """Get or create Google service instance."""
        if self._google_service is None and "google" in self.connections:
            from app.services.integrations.google_service import GoogleService
            creds = self.connections["google"]
            self._google_service = GoogleService(
                access_token=creds.get("access_token"),
                refresh_token=creds.get("refresh_token"),
            )
        return self._google_service
    
    async def get_slack_service(self):
        """Get or create Slack service instance."""
        if self._slack_service is None and "slack" in self.connections:
            from app.services.integrations.slack_service import SlackService
            creds = self.connections["slack"]
            self._slack_service = SlackService(
                access_token=creds.get("access_token"),
            )
        return self._slack_service
    
    async def close(self):
        """Close all service connections."""
        if self._google_service:
            await self._google_service.close()
        if self._slack_service:
            await self._slack_service.close()
    
    async def execute(
        self,
        node_type: str,
        parameters: dict[str, Any],
        input_data: dict[str, Any],
        is_test: bool = False
    ) -> dict[str, Any]:
        """Execute a single node and return results."""
        executors = {
            "start_manual": self._execute_start,
            "start_form": self._execute_start,
            "start_webhook": self._execute_start,
            "start_schedule": self._execute_start,
            "send_email": self._execute_send_email,
            "append_row": self._execute_append_row,
            "read_sheet": self._execute_read_sheet,
            "delay": self._execute_delay,
            "send_notification": self._execute_notification,
            "send_slack": self._execute_send_slack,
            "http_request": self._execute_http_request,
            "condition": self._execute_condition,
            "transform": self._execute_transform,
        }
        
        executor = executors.get(node_type, self._execute_default)
        return await executor(parameters, input_data, is_test)
    
    async def _execute_start(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Start node just passes through data."""
        return {
            "success": True,
            "output": input_data,
            "logs": f"[{datetime.utcnow().isoformat()}] Workflow started\n"
        }
    
    async def _execute_send_email(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Send email via Gmail API or SMTP."""
        to = params.get("to", input_data.get("email", ""))
        subject = params.get("subject", "No subject")
        body = params.get("body", "")
        
        # Interpolate variables
        subject = _interpolate(subject, input_data)
        body = _interpolate(body, input_data)
        to = _interpolate(to, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Sending email\n"
        logs += f"  To: {to}\n"
        logs += f"  Subject: {subject}\n"
        
        if is_test:
            logs += "  Email NOT sent (test mode)\n"
            return {
                "success": True,
                "output": {**input_data, "email_sent": False, "email_to": to, "email_subject": subject},
                "logs": logs
            }
        
        # Try Gmail API first
        google = await self.get_google_service()
        if google:
            try:
                result = await google.send_email(to, subject, body)
                logs += f"  ✅ Email sent via Gmail (ID: {result.get('id', 'unknown')})\n"
                return {
                    "success": True,
                    "output": {**input_data, "email_sent": True, "email_to": to, "email_subject": subject, "message_id": result.get("id")},
                    "logs": logs
                }
            except Exception as e:
                logs += f"  ⚠️ Gmail failed: {str(e)}\n"
        
        # Fallback to SMTP if configured
        from app.services.integrations.email_service import EmailService
        email_service = EmailService()
        if email_service.is_configured:
            try:
                email_service.send_email(to, subject, body)
                logs += "  ✅ Email sent via SMTP\n"
                return {
                    "success": True,
                    "output": {**input_data, "email_sent": True, "email_to": to, "email_subject": subject},
                    "logs": logs
                }
            except Exception as e:
                logs += f"  ⚠️ SMTP failed: {str(e)}\n"
        
        # Mock mode - no real email provider
        logs += "  ⚠️ No email provider configured - email simulated\n"
        return {
            "success": True,
            "output": {**input_data, "email_sent": True, "email_to": to, "email_subject": subject, "simulated": True},
            "logs": logs
        }
    
    async def _execute_append_row(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Append row to Google Sheets."""
        spreadsheet = params.get("spreadsheet", "Untitled Spreadsheet")
        spreadsheet_id = params.get("spreadsheet_id")
        sheet_name = params.get("sheet_name", "Sheet1")
        columns = params.get("columns", [])
        
        # Build row data
        row_data = []
        for col in columns:
            value = _interpolate(str(col.get("value", "")), input_data)
            row_data.append(value)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Adding row to spreadsheet\n"
        logs += f"  Spreadsheet: {spreadsheet}\n"
        logs += f"  Row data: {row_data}\n"
        
        if is_test:
            logs += "  Row NOT added (test mode)\n"
            return {
                "success": True,
                "output": {**input_data, "row_added": False, "spreadsheet": spreadsheet, "row_data": row_data},
                "logs": logs
            }
        
        google = await self.get_google_service()
        if google:
            try:
                # Find or create spreadsheet by name
                if not spreadsheet_id:
                    spreadsheet_id = await google.find_or_create_spreadsheet(spreadsheet)
                    logs += f"  Found/created spreadsheet ID: {spreadsheet_id}\n"
                
                result = await google.append_row(spreadsheet_id, row_data, sheet_name)
                logs += f"  ✅ Row added successfully\n"
                return {
                    "success": True,
                    "output": {**input_data, "row_added": True, "spreadsheet": spreadsheet, "spreadsheet_id": spreadsheet_id, "row_data": row_data},
                    "logs": logs
                }
            except Exception as e:
                logs += f"  ❌ Failed: {str(e)}\n"
                return {
                    "success": False,
                    "output": input_data,
                    "logs": logs,
                    "error": str(e)
                }
        
        # No Google connection - simulate
        logs += "  ⚠️ Google Sheets not connected - row simulated\n"
        return {
            "success": True,
            "output": {**input_data, "row_added": True, "spreadsheet": spreadsheet, "row_data": row_data, "simulated": True},
            "logs": logs
        }
    
    async def _execute_read_sheet(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Read data from Google Sheets."""
        spreadsheet_id = params.get("spreadsheet_id")
        range_name = params.get("range", "Sheet1")
        
        logs = f"[{datetime.utcnow().isoformat()}] Reading from spreadsheet\n"
        logs += f"  Range: {range_name}\n"
        
        google = await self.get_google_service()
        if google and spreadsheet_id:
            try:
                values = await google.get_sheet_values(spreadsheet_id, range_name)
                logs += f"  ✅ Read {len(values)} rows\n"
                return {
                    "success": True,
                    "output": {**input_data, "sheet_data": values, "row_count": len(values)},
                    "logs": logs
                }
            except Exception as e:
                logs += f"  ❌ Failed: {str(e)}\n"
                return {"success": False, "output": input_data, "logs": logs, "error": str(e)}
        
        logs += "  ⚠️ Google Sheets not connected\n"
        return {"success": False, "output": input_data, "logs": logs, "error": "Google Sheets not connected"}
    
    async def _execute_send_slack(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Send message to Slack."""
        channel = params.get("channel", "#general")
        message = params.get("message", "")
        
        message = _interpolate(message, input_data)
        channel = _interpolate(channel, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Sending Slack message\n"
        logs += f"  Channel: {channel}\n"
        logs += f"  Message: {message[:100]}{'...' if len(message) > 100 else ''}\n"
        
        if is_test:
            logs += "  Message NOT sent (test mode)\n"
            return {
                "success": True,
                "output": {**input_data, "slack_sent": False, "channel": channel},
                "logs": logs
            }
        
        slack = await self.get_slack_service()
        if slack:
            try:
                # Find channel by name
                channel_info = await slack.find_channel_by_name(channel)
                channel_id = channel_info["id"] if channel_info else channel
                
                result = await slack.send_message(channel_id, message)
                logs += f"  ✅ Message sent (ts: {result.get('ts', 'unknown')})\n"
                return {
                    "success": True,
                    "output": {**input_data, "slack_sent": True, "channel": channel, "message_ts": result.get("ts")},
                    "logs": logs
                }
            except Exception as e:
                logs += f"  ❌ Failed: {str(e)}\n"
                return {"success": False, "output": input_data, "logs": logs, "error": str(e)}
        
        logs += "  ⚠️ Slack not connected - message simulated\n"
        return {
            "success": True,
            "output": {**input_data, "slack_sent": True, "channel": channel, "simulated": True},
            "logs": logs
        }
    
    async def _execute_delay(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Wait for a specified duration."""
        duration = params.get("duration", 60)
        unit = params.get("unit", "seconds")
        
        # Convert to seconds
        multipliers = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}
        seconds = duration * multipliers.get(unit, 1)
        
        logs = f"[{datetime.utcnow().isoformat()}] Delay step\n"
        logs += f"  Duration: {duration} {unit}\n"
        
        if is_test or seconds > 300:  # Skip delays > 5 mins in any case
            logs += f"  Skipped delay ({'test mode' if is_test else 'too long'})\n"
        else:
            logs += f"  Waiting {seconds} seconds...\n"
            await asyncio.sleep(seconds)
            logs += f"  Done waiting\n"
        
        return {"success": True, "output": input_data, "logs": logs}
    
    async def _execute_notification(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Send a notification (internal)."""
        message = params.get("message", "Notification")
        message = _interpolate(message, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Notification\n"
        logs += f"  Message: {message}\n"
        logs += "  ✅ Notification logged\n"
        
        return {
            "success": True,
            "output": {**input_data, "notification_sent": True, "notification_message": message},
            "logs": logs
        }
    
    async def _execute_http_request(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Make an HTTP request."""
        import httpx
        
        method = params.get("method", "GET").upper()
        url = params.get("url", "")
        headers = params.get("headers", {})
        body = params.get("body")
        
        url = _interpolate(url, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}HTTP Request\n"
        logs += f"  Method: {method}\n"
        logs += f"  URL: {url}\n"
        
        if is_test:
            logs += "  Request NOT made (test mode)\n"
            return {"success": True, "output": input_data, "logs": logs}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url, headers=headers, json=body if body else None)
                logs += f"  Status: {response.status_code}\n"
                
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                return {
                    "success": response.status_code < 400,
                    "output": {**input_data, "http_response": response_data, "http_status": response.status_code},
                    "logs": logs
                }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "output": input_data, "logs": logs, "error": str(e)}
    
    async def _execute_condition(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Evaluate a condition."""
        field = params.get("field", "")
        operator = params.get("operator", "equals")
        value = params.get("value", "")
        
        field_value = input_data.get(field, "")
        value = _interpolate(str(value), input_data)
        
        result = False
        if operator == "equals":
            result = str(field_value) == str(value)
        elif operator == "not_equals":
            result = str(field_value) != str(value)
        elif operator == "contains":
            result = str(value) in str(field_value)
        elif operator == "greater_than":
            result = float(field_value) > float(value)
        elif operator == "less_than":
            result = float(field_value) < float(value)
        elif operator == "is_empty":
            result = not field_value
        elif operator == "is_not_empty":
            result = bool(field_value)
        
        logs = f"[{datetime.utcnow().isoformat()}] Condition check\n"
        logs += f"  {field} {operator} {value}\n"
        logs += f"  Result: {result}\n"
        
        return {
            "success": True,
            "output": {**input_data, "condition_result": result},
            "logs": logs,
            "branch": "true" if result else "false"
        }
    
    async def _execute_transform(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Transform data."""
        transforms = params.get("transforms", [])
        output = dict(input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] Transforming data\n"
        
        for t in transforms:
            target = t.get("target")
            source = t.get("source")
            operation = t.get("operation", "copy")
            
            if source and target:
                value = input_data.get(source, "")
                
                if operation == "copy":
                    output[target] = value
                elif operation == "uppercase":
                    output[target] = str(value).upper()
                elif operation == "lowercase":
                    output[target] = str(value).lower()
                elif operation == "trim":
                    output[target] = str(value).strip()
                elif operation == "template":
                    template = t.get("template", "")
                    output[target] = _interpolate(template, input_data)
                
                logs += f"  {target} = {output[target]}\n"
        
        return {"success": True, "output": output, "logs": logs}
    
    async def _execute_default(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Default executor for unknown node types."""
        logs = f"[{datetime.utcnow().isoformat()}] Unknown node type\n"
        logs += f"  Parameters: {params}\n"
        return {"success": True, "output": input_data, "logs": logs}


def _interpolate(template: str, data: dict) -> str:
    """Replace {{variable}} with values from data."""
    if not template:
        return template
    result = template
    for key, value in data.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


# Backward compatibility - sync wrapper
def execute_node(
    node_type: str,
    parameters: dict[str, Any],
    input_data: dict[str, Any],
    is_test: bool = False,
    connections: Optional[dict] = None
) -> dict[str, Any]:
    """Execute a single node (sync wrapper for backward compatibility)."""
    executor = NodeExecutor(connections)
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(
            executor.execute(node_type, parameters, input_data, is_test)
        )
        return result
    finally:
        loop.run_until_complete(executor.close())
        loop.close()
