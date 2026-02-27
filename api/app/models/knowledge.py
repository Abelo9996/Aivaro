from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)  # business_info, policies, pricing, contacts, deadlines, custom
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(Integer, default=0)  # higher = more important, injected first
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", backref="knowledge_entries")
