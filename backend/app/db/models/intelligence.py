from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.utils.helper import generate_unique_id


class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(String, primary_key=True, default=generate_unique_id)

    name = Column(String(255), nullable=False)
    key = Column(String(100), unique=True, nullable=False)  # e.g. human, trees
    description = Column(Text, nullable=True)

    # Multi-level support
    levels = Column(JSON, default=list)
    # Example: ["detection", "gender_age", "activity"]

    provider = Column(String(50), default="local")
    # local / openai / gemini / groq / grok

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AIRequest(Base):
    __tablename__ = "ai_requests"

    id = Column(String, primary_key=True, default=generate_unique_id)

    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    model_id = Column(String, ForeignKey("ai_models.id"), nullable=True)

    application = Column(String(100), nullable=True)
    level = Column(String(50), nullable=True)

    input_data = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    enhanced_result = Column(Text, nullable=True)

    status = Column(String(50), default="pending")
    # pending / processing / completed / failed

    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User")
    model = relationship("AIModel")