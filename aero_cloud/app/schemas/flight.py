from typing import Literal

from pydantic import BaseModel, Field


FlightModeName = Literal["position_hold", "waypoint_patrol", "orbit", "acro"]


class FlightModeSelection(BaseModel):
    mode: FlightModeName


class ControlInput(BaseModel):
    roll: float = Field(ge=-1, le=1)
    pitch: float = Field(ge=-1, le=1)
    yaw: float = Field(ge=-1, le=1)
    throttle: float = Field(ge=0, le=1)


class FlightStatus(BaseModel):
    session_active: bool
    armed: bool
    arming_available: bool
    selected_mode: FlightModeName | None
    control_available: bool
    ready_for_flight: bool
    detail: str