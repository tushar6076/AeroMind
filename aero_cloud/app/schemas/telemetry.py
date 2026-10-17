from pydantic import BaseModel


class TelemetrySnapshot(BaseModel):
    timestamp: float
    link_quality: int | None = None
    battery_voltage: float | None = None
    battery_percent: float | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    gps_satellites: int | None = None
    roll_degrees: float | None = None
    pitch_degrees: float | None = None
    yaw_degrees: float | None = None


class TelemetryEnvelope(BaseModel):
    type: str = "telemetry"
    data: TelemetrySnapshot