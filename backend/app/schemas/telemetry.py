from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TelemetryData(BaseModel):
    battery: Optional[float] = None
    altitude: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    speed: Optional[float] = None
    rain: Optional[bool] = None
    lidar: Optional[float] = None
    ultrasonic: Optional[float] = None
    flight_mode: Optional[str] = None
    signal: Optional[float] = None
    timestamp: Optional[datetime] = None

class SDPPayload(BaseModel):
    sdp: str
    type: str  # "offer" or "answer"
    target: Optional[str] = "drone"  # "drone" or user_id


class ICECandidatePayload(BaseModel):
    candidate: dict
    target: Optional[str] = "drone"


class MessageResponse(BaseModel):
    message: str
    success: bool = True