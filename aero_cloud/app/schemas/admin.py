from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class AdminUserResponse(BaseModel):
    id: str
    full_name: Optional[str]
    email: EmailStr
    role: str
    is_active: bool
    is_approved: bool
    is_verified: bool
    last_active: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str


class ForcedControlRequest(BaseModel):
    reason: Optional[str] = None


class AIModelUpdateRequest(BaseModel):
    is_active: bool