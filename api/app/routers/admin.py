"""
Admin dashboard API — metrics, users, workflows, executions.
Only accessible by users with is_admin=True.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User
from app.models.workflow import Workflow
from app.models.execution import Execution, ExecutionNode
from app.models.chat import ChatConversation, ChatMessage
from app.models.connection import Connection
from app.models.knowledge import KnowledgeEntry
from app.models.audit_log import AuditLog
from app.routers.auth import get_current_user

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


@router.get("/stats")
async def get_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """High-level platform stats for the admin dashboard."""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # --- Users ---
    total_users = db.query(func.count(User.id)).scalar() or 0
    users_today = db.query(func.count(User.id)).filter(User.created_at >= today_start).scalar() or 0
    users_this_week = db.query(func.count(User.id)).filter(User.created_at >= week_ago).scalar() or 0
    users_this_month = db.query(func.count(User.id)).filter(User.created_at >= month_ago).scalar() or 0

    # Plan breakdown
    plan_counts = dict(
        db.query(User.plan, func.count(User.id)).group_by(User.plan).all()
    )

    # Verified vs unverified
    verified_count = db.query(func.count(User.id)).filter(User.email_verified == True).scalar() or 0

    # --- Workflows ---
    total_workflows = db.query(func.count(Workflow.id)).scalar() or 0
    active_workflows = db.query(func.count(Workflow.id)).filter(Workflow.is_active == True).scalar() or 0
    workflows_this_week = db.query(func.count(Workflow.id)).filter(Workflow.created_at >= week_ago).scalar() or 0

    # --- Executions ---
    total_executions = db.query(func.count(Execution.id)).scalar() or 0
    executions_today = db.query(func.count(Execution.id)).filter(Execution.started_at >= today_start).scalar() or 0
    executions_this_week = db.query(func.count(Execution.id)).filter(Execution.started_at >= week_ago).scalar() or 0

    exec_status_counts = dict(
        db.query(Execution.status, func.count(Execution.id)).group_by(Execution.status).all()
    )

    # --- Chat ---
    total_conversations = db.query(func.count(ChatConversation.id)).scalar() or 0
    total_messages = db.query(func.count(ChatMessage.id)).scalar() or 0
    messages_today = db.query(func.count(ChatMessage.id)).filter(ChatMessage.created_at >= today_start).scalar() or 0

    # --- Connections ---
    total_connections = db.query(func.count(Connection.id)).scalar() or 0

    # --- Knowledge ---
    total_knowledge = 0
    try:
        total_knowledge = db.query(func.count(KnowledgeEntry.id)).scalar() or 0
    except Exception:
        pass

    # --- Daily active users (users who sent a chat message or ran an execution today) ---
    dau_chat = db.query(func.count(distinct(ChatMessage.user_id))).filter(
        ChatMessage.created_at >= today_start
    ).scalar() or 0

    # Users who had executions today (via workflow ownership)
    dau_exec = db.query(func.count(distinct(Workflow.user_id))).join(
        Execution, Execution.workflow_id == Workflow.id
    ).filter(Execution.started_at >= today_start).scalar() or 0

    # WAU
    wau_chat = db.query(func.count(distinct(ChatMessage.user_id))).filter(
        ChatMessage.created_at >= week_ago
    ).scalar() or 0

    # --- Signups over last 30 days (daily) ---
    signup_trend = []
    for i in range(30):
        day_start = (now - timedelta(days=29 - i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = db.query(func.count(User.id)).filter(
            User.created_at >= day_start, User.created_at < day_end
        ).scalar() or 0
        signup_trend.append({"date": day_start.strftime("%Y-%m-%d"), "count": count})

    # --- Executions over last 30 days (daily) ---
    exec_trend = []
    for i in range(30):
        day_start = (now - timedelta(days=29 - i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = db.query(func.count(Execution.id)).filter(
            Execution.started_at >= day_start, Execution.started_at < day_end
        ).scalar() or 0
        exec_trend.append({"date": day_start.strftime("%Y-%m-%d"), "count": count})

    return {
        "users": {
            "total": total_users,
            "today": users_today,
            "this_week": users_this_week,
            "this_month": users_this_month,
            "verified": verified_count,
            "unverified": total_users - verified_count,
            "by_plan": plan_counts,
        },
        "activity": {
            "dau": max(dau_chat, dau_exec),
            "wau": wau_chat,
        },
        "workflows": {
            "total": total_workflows,
            "active": active_workflows,
            "this_week": workflows_this_week,
        },
        "executions": {
            "total": total_executions,
            "today": executions_today,
            "this_week": executions_this_week,
            "by_status": exec_status_counts,
        },
        "chat": {
            "conversations": total_conversations,
            "messages": total_messages,
            "messages_today": messages_today,
        },
        "connections": {
            "total": total_connections,
        },
        "knowledge": {
            "total": total_knowledge,
        },
        "trends": {
            "signups_30d": signup_trend,
            "executions_30d": exec_trend,
        },
    }


@router.get("/users")
async def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all users with their usage stats."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        workflow_count = db.query(func.count(Workflow.id)).filter(Workflow.user_id == u.id).scalar() or 0
        active_wf = db.query(func.count(Workflow.id)).filter(Workflow.user_id == u.id, Workflow.is_active == True).scalar() or 0
        exec_count = db.query(func.count(Execution.id)).join(Workflow).filter(Workflow.user_id == u.id).scalar() or 0
        msg_count = db.query(func.count(ChatMessage.id)).filter(ChatMessage.user_id == u.id).scalar() or 0
        conn_count = db.query(func.count(Connection.id)).filter(Connection.user_id == u.id).scalar() or 0
        last_active = db.query(func.max(ChatMessage.created_at)).filter(ChatMessage.user_id == u.id).scalar()

        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "plan": u.plan,
            "email_verified": u.email_verified,
            "onboarding_completed": u.onboarding_completed,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "trial_days_left": u.trial_days_left if u.is_trial else None,
            "workflows": workflow_count,
            "active_workflows": active_wf,
            "executions": exec_count,
            "total_runs_used": u.total_runs_used,
            "messages": msg_count,
            "connections": conn_count,
            "last_active": last_active.isoformat() if last_active else None,
            "is_admin": getattr(u, "is_admin", False),
        })

    return result


@router.get("/recent-activity")
async def recent_activity(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    """Recent executions with user + workflow info."""
    execs = (
        db.query(Execution, Workflow, User)
        .join(Workflow, Execution.workflow_id == Workflow.id)
        .join(User, Workflow.user_id == User.id)
        .order_by(Execution.started_at.desc())
        .limit(limit)
        .all()
    )
    result = []
    for ex, wf, user in execs:
        result.append({
            "id": ex.id,
            "workflow_name": wf.name,
            "user_email": user.email,
            "user_name": user.full_name,
            "status": ex.status,
            "started_at": ex.started_at.isoformat() if ex.started_at else None,
            "completed_at": ex.completed_at.isoformat() if ex.completed_at else None,
            "is_test": ex.is_test,
            "error": ex.error,
        })
    return result


@router.post("/bootstrap")
async def bootstrap_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Promote current user to admin if their email is in ADMIN_EMAILS env var.
    Fallback: first user in the database gets admin if no ADMIN_EMAILS set.
    """
    import os
    admin_emails_raw = os.environ.get("ADMIN_EMAILS", "")
    admin_emails = [e.strip().lower() for e in admin_emails_raw.split(",") if e.strip()]

    allowed = False
    if admin_emails:
        allowed = current_user.email.lower() in admin_emails
    else:
        # No env var — allow first user
        first_user = db.query(User).order_by(User.created_at.asc()).first()
        if first_user and first_user.id == current_user.id:
            allowed = True

    if not allowed:
        raise HTTPException(status_code=403, detail="Not authorized to become admin")

    current_user.is_admin = True
    db.commit()
    return {"message": "Admin access granted", "email": current_user.email}
