from pydantic import BaseModel, Field
from typing import Optional, List, Any


class AIModelInfo(BaseModel):
    id: str  # <--- Added
    key: str
    name: str
    description: Optional[str] = None
    levels: List[str] = []
    provider: Optional[str] = "local"  # <--- Added
    is_active: bool = True

    class Config:
        from_attributes = True


class IdentifyRequest(BaseModel):
    application: str = Field(..., description="e.g. human, trees, animals")
    level: int = Field(1, ge=1, le=3)
    data: Any
    enhance: bool = True
    preferred_provider: Optional[str] = None


class IdentifyResponse(BaseModel):
    success: bool
    application: str
    level: int
    result: dict
    enhanced: Optional[str] = None
    provider: Optional[str] = None