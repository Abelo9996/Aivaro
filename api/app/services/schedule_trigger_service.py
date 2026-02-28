"""
Schedule Trigger Service - Polls for workflows with start_schedule triggers and runs them at the right time.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Workflow, Execution, User

logger = logging.getLogger(__name__)

# Track last-run timestamps per workflow to avoid duplicate triggers within the same window
_last_triggered: dict[str, str] = {}  # workflow_id -> "YYYY-MM-DD" or "YYYY-MM-DD HH:MM"


def _should_run_now(node_params: dict, now: datetime) -> bool:
    """
    Check if a schedule trigger should fire right now.
    
    Supports:
      - frequency: "daily", "weekly", "monthly", "once"
      - time: "HH:MM" (24h format)
      - timezone: e.g. "America/Los_Angeles" (defaults to UTC)
      - day_of_week: "monday", "tuesday", etc. (for weekly)
      - date: "YYYY-MM-DD" (for once)
    
    We check within a 2-minute window to account for polling interval.
    """
    time_str = node_params.get("time", "")
    frequency = node_params.get("frequency", "daily").lower()
    tz_str = node_params.get("timezone", "America/Los_Angeles")
    
    if not time_str:
        return False
    
    try:
        tz = ZoneInfo(tz_str)
    except Exception:
        tz = ZoneInfo("America/Los_Angeles")
    
    now_local = now.astimezone(tz)
    
    # Parse target time
    try:
        parts = time_str.replace(".", ":").split(":")
        target_hour = int(parts[0])
        target_minute = int(parts[1]) if len(parts) > 1 else 0
    except (ValueError, IndexError):
        return False
    
    # Check if we're within 2 minutes of the target time
    target_today = now_local.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    diff = abs((now_local - target_today).total_seconds())
    if diff > 120:  # 2-minute window
        return False
    
    # Check frequency-specific conditions
    if frequency == "daily":
        return True
    
    if frequency == "weekly":
        day = node_params.get("day_of_week", "").lower()
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if day in days:
            return now_local.weekday() == days.index(day)
        return True  # If no day specified, run daily
    
    if frequency == "monthly":
        day_of_month = node_params.get("day_of_month")
        if day_of_month:
            try:
                return now_local.day == int(day_of_month)
            except ValueError:
                pass
        return now_local.day == 1  # Default to 1st of month
    
    if frequency == "once":
        date_str = node_params.get("date", "")
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                return now_local.date() == target_date
            except ValueError:
                pass
        return True  # If no date, run once now
    
    return False


async def poll_schedule_triggers():
    """Check all active workflows for schedule triggers that should fire now."""
    db = SessionLocal()
    try:
        workflows = db.query(Workflow).filter(
            Workflow.is_active == True,
            Workflow.is_agent_task == False,
        ).all()
        
        now = datetime.now(ZoneInfo("UTC"))
        triggered = []
        
        for workflow in workflows:
            schedule_nodes = [
                n for n in (workflow.nodes or [])
                if n.get("type") == "start_schedule"
            ]
            
            if not schedule_nodes:
                continue
            
            node = schedule_nodes[0]
            params = node.get("params", node.get("data", {}))
            
            if not _should_run_now(params, now):
                continue
            
            # Dedup: don't trigger same workflow twice in same minute window
            freq = params.get("frequency", "daily").lower()
            if freq == "once":
                dedup_key = f"{workflow.id}:once:{params.get('date', '')}:{params.get('time', '')}"
            else:
                dedup_key = f"{workflow.id}:{now.strftime('%Y-%m-%d-%H-%M')}"
            
            if dedup_key in _last_triggered:
                continue
            _last_triggered[dedup_key] = True
            
            # Clean old dedup keys (keep last 1000)
            if len(_last_triggered) > 1000:
                keys = list(_last_triggered.keys())
                for k in keys[:500]:
                    del _last_triggered[k]
            
            # Run the workflow
            try:
                user = db.query(User).filter(User.id == workflow.user_id).first()
                if not user:
                    continue
                
                from app.services.workflow_runner import WorkflowRunner
                
                execution = Execution(
                    workflow_id=workflow.id,
                    status="running",
                    is_test=False,
                    trigger_data={"trigger": "schedule", "time": now.isoformat()},
                )
                db.add(execution)
                db.commit()
                db.refresh(execution)
                
                runner = WorkflowRunner(
                    workflow=workflow,
                    execution=execution,
                    db=db,
                )
                result = runner.run(trigger_data={"trigger": "schedule", "time": now.isoformat()})
                
                logger.info(f"[Schedule Trigger] Ran workflow '{workflow.name}' (id={workflow.id}) -> status={result.status}")
                triggered.append({
                    "workflow_id": workflow.id,
                    "workflow_name": workflow.name,
                    "execution_id": execution.id,
                    "status": result.status,
                })
                
                # If frequency is "once", deactivate the workflow after running
                if freq == "once":
                    workflow.is_active = False
                    db.commit()
                    logger.info(f"[Schedule Trigger] Deactivated one-time workflow '{workflow.name}'")
                    
            except Exception as e:
                logger.error(f"[Schedule Trigger] Error running workflow {workflow.id}: {e}")
        
        return triggered
        
    except Exception as e:
        logger.error(f"[Schedule Trigger] Poll error: {e}")
        return []
    finally:
        db.close()


async def poll_schedule_triggers_task():
    """Background task that checks schedule triggers every 60 seconds."""
    while True:
        try:
            results = await poll_schedule_triggers()
            if results:
                print(f"[Schedule Trigger] Triggered {len(results)} workflow(s)")
        except Exception as e:
            print(f"[Schedule Trigger] Error: {e}")
        
        await asyncio.sleep(60)
