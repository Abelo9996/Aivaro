"""Plan limit enforcement for trial and paid users."""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User, Workflow, KnowledgeEntry
from app.models.user import TRIAL_DURATION_DAYS


def check_trial_active(user: User):
    """Raise 403 if trial has expired and user hasn't upgraded."""
    if user.is_trial and user.trial_expired:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "trial_expired",
                "message": f"Your {TRIAL_DURATION_DAYS}-day free trial has ended. Upgrade to continue using Aivaro.",
                "trial_days_left": 0,
                "plan": "trial",
            },
        )


def check_can_activate_workflow(user: User, db: Session):
    """Check if user can activate another workflow."""
    check_trial_active(user)
    limits = user.limits
    active_count = db.query(Workflow).filter(
        Workflow.user_id == user.id,
        Workflow.is_active == True,
        Workflow.is_agent_task == False,
    ).count()
    if active_count >= limits["max_active_workflows"]:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "workflow_limit",
                "message": f"Free trial allows {limits['max_active_workflows']} active workflow. Upgrade for unlimited workflows.",
                "limit": limits["max_active_workflows"],
                "current": active_count,
                "plan": user.plan,
            },
        )


def check_can_run_workflow(user: User):
    """Check if user has remaining runs."""
    check_trial_active(user)
    limits = user.limits
    if user.total_runs_used >= limits["max_total_runs"]:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "run_limit",
                "message": f"Free trial allows {limits['max_total_runs']} workflow runs. Upgrade for unlimited runs.",
                "limit": limits["max_total_runs"],
                "used": user.total_runs_used,
                "plan": user.plan,
            },
        )


def check_can_use_agent(user: User):
    """Check if user can use agent tasks."""
    check_trial_active(user)
    if not user.limits["allow_agent_tasks"]:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "agent_locked",
                "message": "AI Agent tasks are available on paid plans. Upgrade to unlock.",
                "plan": user.plan,
            },
        )


def check_can_add_knowledge(user: User, db: Session):
    """Check if user can add more knowledge entries."""
    check_trial_active(user)
    limits = user.limits
    count = db.query(KnowledgeEntry).filter(KnowledgeEntry.user_id == user.id).count()
    if count >= limits["max_knowledge_entries"]:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "knowledge_limit",
                "message": f"Free trial allows {limits['max_knowledge_entries']} knowledge entries. Upgrade for unlimited.",
                "limit": limits["max_knowledge_entries"],
                "current": count,
                "plan": user.plan,
            },
        )


def check_can_import_file(user: User):
    """Check if user can import files."""
    check_trial_active(user)
    if not user.limits["allow_file_import"]:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "import_locked",
                "message": "File import is available on paid plans. Upgrade to unlock.",
                "plan": user.plan,
            },
        )


def increment_run_count(user: User, db: Session):
    """Increment the user's total run count."""
    user.total_runs_used = (user.total_runs_used or 0) + 1
    db.commit()


def get_usage_summary(user: User, db: Session) -> dict:
    """Get current usage vs limits."""
    limits = user.limits
    active_wf = db.query(Workflow).filter(
        Workflow.user_id == user.id,
        Workflow.is_active == True,
        Workflow.is_agent_task == False,
    ).count()
    knowledge_count = db.query(KnowledgeEntry).filter(KnowledgeEntry.user_id == user.id).count()

    return {
        "plan": user.plan,
        "is_trial": user.is_trial,
        "trial_expired": user.trial_expired,
        "trial_days_left": user.trial_days_left,
        "usage": {
            "active_workflows": {"used": active_wf, "limit": limits["max_active_workflows"]},
            "total_runs": {"used": user.total_runs_used or 0, "limit": limits["max_total_runs"]},
            "knowledge_entries": {"used": knowledge_count, "limit": limits["max_knowledge_entries"]},
        },
        "features": {
            "agent_tasks": limits["allow_agent_tasks"],
            "file_import": limits["allow_file_import"],
        },
    }
