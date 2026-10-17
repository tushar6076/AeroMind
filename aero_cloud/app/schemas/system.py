from pydantic import BaseModel


class SystemStatus(BaseModel):
    backend_online: bool
    environment: str
    companion_temperature_c: float | None


class ReadinessCheck(BaseModel):
    name: str
    ready: bool
    detail: str


class HealthResponse(BaseModel):
    backend_online: bool
    elrs_configured: bool
    elrs_connected: bool
    elrs_link_quality: int | None
    flight_controller_telemetry: bool
    gps_satellites: int | None
    battery_percent: float | None
    imu_available: bool
    companion_temperature_c: float | None
    video_input_configured: bool
    video_input_available: bool
    video_streaming: bool
    ready_for_flight: bool
    checks: list[ReadinessCheck]