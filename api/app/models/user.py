from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from app.database import Base

TRIAL_DURATION_DAYS = 7

# Trial limits
TRIAL_LIMITS = {
    "max_active_workflows": 1,
    "max_total_runs": 10,
    "max_knowledge_entries": 3,
    "allow_agent_tasks": False,
    "allow_file_import": False,
}

# Paid plan (no limits enforced in code for now)
PAID_LIMITS = {
    "max_active_workflows": 999,
    "max_total_runs": 999999,
    "max_knowledge_entries": 999,
    "allow_agent_tasks": True,
    "allow_file_import": True,
}


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    onboarding_completed = Column(Boolean, default=False)
    plan = Column(String, default="trial")  # trial, starter, growth, pro
    trial_started_at = Column(DateTime, default=datetime.utcnow)
    total_runs_used = Column(Integer, default=0)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workflows = relationship("Workflow", back_populates="user")
    connections = relationship("Connection", back_populates="user")

    @property
    def is_trial(self) -> bool:
        return self.plan == "trial"

    @property
    def trial_expired(self) -> bool:
        if not self.is_trial:
            return False
        if not self.trial_started_at:
            return True
        return datetime.utcnow() > self.trial_started_at + timedelta(days=TRIAL_DURATION_DAYS)

    @property
    def trial_days_left(self) -> int:
        if not self.is_trial or not self.trial_started_at:
            return 0
        delta = (self.trial_started_at + timedelta(days=TRIAL_DURATION_DAYS)) - datetime.utcnow()
        return max(0, delta.days)

    @property
    def limits(self) -> dict:
        if self.is_trial and not self.trial_expired:
            return TRIAL_LIMITS
        if self.is_trial and self.trial_expired:
            # Expired trial = everything locked
            return {
                "max_active_workflows": 0,
                "max_total_runs": 0,
                "max_knowledge_entries": 0,
                "allow_agent_tasks": False,
                "allow_file_import": False,
            }
        return PAID_LIMITS
