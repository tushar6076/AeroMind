from pydantic import BaseModel, Field


class JoystickLeftRequest(BaseModel):
    throttle: float = Field(..., ge=0.0, le=1.0)
    yaw: float = Field(..., ge=-1.0, le=1.0)


class JoystickRightRequest(BaseModel):
    pitch: float = Field(..., ge=-1.0, le=1.0)
    roll: float = Field(..., ge=-1.0, le=1.0)


class MessageResponse(BaseModel):
    message: str
    success: bool = True