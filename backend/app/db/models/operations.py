from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Text, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.utils.helper import generate_unique_id


class Connection(Base):
    __tablename__ = "connections"

    id = Column(String, primary_key=True, default=generate_unique_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    status = Column(String(50), default="disconnected")  
    # possible values: connected, disconnected, busy

    is_active_controller = Column(Boolean, default=False)

    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(String, primary_key=True, default=generate_unique_id)

    event_type = Column(String(100), nullable=False)
    # examples: low_battery, obstacle_detected, rain_detected, emergency_stop

    severity = Column(String(50), default="info")
    # info / warning / critical

    message = Column(Text, nullable=True)
    value = Column(Float, nullable=True)  # optional numeric value (e.g. battery %)

    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    connection_id = Column(String, ForeignKey("connections.id"), nullable=True)

    created_at = Column(DateTime, default=func.now())