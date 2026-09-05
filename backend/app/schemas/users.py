from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserProfile(BaseModel):
    id: str
    full_name: Optional[str]
    email: EmailStr
    role: str
    is_approved: bool
    last_active: Optional[datetime]

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)


class DeviceResponse(BaseModel):
    id: str
    device_id: str
    device_info: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str