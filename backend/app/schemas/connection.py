from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConnectionStatusResponse(BaseModel):
    is_connected: bool
    is_active_controller: bool
    active_controller_id: Optional[str] = None
    message: str


class ConnectionHistoryItem(BaseModel):
    id: str
    status: str
    is_active_controller: bool
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str