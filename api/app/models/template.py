from sqlalchemy import Column, String, DateTime, JSON, Text
from datetime import datetime
import uuid

from app.database import Base


class Template(Base):
    __tablename__ = "templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    business_types = Column(JSON, default=list)
    nodes = Column(JSON, default=list)
    edges = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
