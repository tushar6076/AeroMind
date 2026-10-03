from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.utils.helper import generate_unique_id


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_unique_id)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    role = Column(String(50), default="user")  # user / admin
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)

    last_active = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    admin_logs = relationship("AdminLog", back_populates="admin", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, default=generate_unique_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    device_id = Column(String(255), nullable=False)
    device_info = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    last_login = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="devices")


class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(String, primary_key=True, default=generate_unique_id)
    admin_id = Column(String, ForeignKey("users.id"), nullable=False)

    action = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=True)
    target_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)

    created_at = Column(DateTime, default=func.now())

    admin = relationship("User", back_populates="admin_logs")