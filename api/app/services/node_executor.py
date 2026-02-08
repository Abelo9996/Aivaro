from typing import Any
from datetime import datetime


def execute_node(
    node_type: str,
    parameters: dict[str, Any],
    input_data: dict[str, Any],
    is_test: bool = False
) -> dict[str, Any]:
    """Execute a single node and return results"""
    
    executors = {
        "start_manual": execute_start,
        "start_form": execute_start,
        "send_email": execute_send_email,
        "append_row": execute_append_row,
        "delay": execute_delay,
        "send_notification": execute_notification,
    }
    
    executor = executors.get(node_type, execute_default)
    return executor(parameters, input_data, is_test)


def execute_start(params: dict, input_data: dict, is_test: bool) -> dict:
    """Start node just passes through data"""
    return {
        "success": True,
        "output": input_data,
        "logs": f"[{datetime.utcnow().isoformat()}] Workflow started\n"
    }


def execute_send_email(params: dict, input_data: dict, is_test: bool) -> dict:
    """Mock email sending"""
    to = params.get("to", input_data.get("email", "unknown@example.com"))
    subject = params.get("subject", "No subject")
    body = params.get("body", "")
    
    # Interpolate variables
    subject = _interpolate(subject, input_data)
    body = _interpolate(body, input_data)
    to = _interpolate(to, input_data)
    
    logs = f"[{datetime.utcnow().isoformat()}] {'[TEST MODE] ' if is_test else ''}Sending email\n"
    logs += f"  To: {to}\n"
    logs += f"  Subject: {subject}\n"
    logs += f"  Body length: {len(body)} characters\n"
    
    if is_test:
        logs += "  Email NOT sent (test mode)\n"
    else:
        logs += "  Email sent successfully (mock)\n"
    
    return {
        "success": True,
        "output": {
            **input_data,
            "email_sent": True,
            "email_to": to,
            "email_subject": subject
        },
        "logs": logs
    }


def execute_append_row(params: dict, input_data: dict, is_test: bool) -> dict:
    """Mock spreadsheet row append"""
    spreadsheet = params.get("spreadsheet", "Untitled Spreadsheet")
    columns = params.get("columns", [])
    
    row_data = []
    for col in columns:
        value = _interpolate(col.get("value", ""), input_data)
        row_data.append(value)
    
    logs = f"[{datetime.utcnow().isoformat()}] {'[TEST MODE] ' if is_test else ''}Adding row to spreadsheet\n"
    logs += f"  Spreadsheet: {spreadsheet}\n"
    logs += f"  Row data: {row_data}\n"
    logs += "  Row added successfully (mock)\n"
    
    return {
        "success": True,
        "output": {
            **input_data,
            "row_added": True,
            "spreadsheet": spreadsheet,
            "row_data": row_data
        },
        "logs": logs
    }


def execute_delay(params: dict, input_data: dict, is_test: bool) -> dict:
    """Mock delay - in test mode, skip the wait"""
    duration = params.get("duration", 60)
    unit = params.get("unit", "seconds")
    
    logs = f"[{datetime.utcnow().isoformat()}] Delay step\n"
    logs += f"  Duration: {duration} {unit}\n"
    
    if is_test:
        logs += "  Skipped delay (test mode)\n"
    else:
        logs += f"  Waiting {duration} {unit}... (mock - instant)\n"
    
    return {
        "success": True,
        "output": input_data,
        "logs": logs
    }


def execute_notification(params: dict, input_data: dict, is_test: bool) -> dict:
    """Mock notification"""
    message = params.get("message", "Notification")
    message = _interpolate(message, input_data)
    
    logs = f"[{datetime.utcnow().isoformat()}] {'[TEST MODE] ' if is_test else ''}Sending notification\n"
    logs += f"  Message: {message}\n"
    logs += "  Notification sent (mock)\n"
    
    return {
        "success": True,
        "output": {**input_data, "notification_sent": True},
        "logs": logs
    }


def execute_default(params: dict, input_data: dict, is_test: bool) -> dict:
    """Default executor for unknown node types"""
    logs = f"[{datetime.utcnow().isoformat()}] Executing unknown node type\n"
    logs += f"  Parameters: {params}\n"
    
    return {
        "success": True,
        "output": input_data,
        "logs": logs
    }


def _interpolate(template: str, data: dict) -> str:
    """Replace {{variable}} with values from data"""
    result = template
    for key, value in data.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result
