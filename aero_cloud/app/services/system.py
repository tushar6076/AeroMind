import os

from app.core.config import settings
from app.schemas.system import HealthResponse, ReadinessCheck, SystemStatus
from app.services.flight.manager import FlightService, settings_temperature
from app.services.video import VideoService


class SystemService:
    def __init__(self, flight: FlightService, video: VideoService) -> None:
        self.flight = flight
        self.video = video

    def status(self) -> SystemStatus:
        return SystemStatus(
            backend_online=True,
            environment=settings.ENVIRONMENT,
            companion_temperature_c=settings_temperature(),
        )

    def health(self) -> HealthResponse:
        temperature = settings_temperature()
        readiness = self.flight.readiness(temperature)
        video_available = bool(
            self.video.device
            and self.video.configured
            and os.access(self.video.device, os.R_OK)
        )
        checks = [
            ReadinessCheck(
                name="Aero Cloud backend",
                ready=True,
                detail="Backend service is responding.",
            ),
            ReadinessCheck(
                name="ELRS transmitter",
                ready=readiness.elrs_connected,
                detail=(
                    f"CRSF link quality {readiness.elrs_link_quality}%."
                    if readiness.elrs_link_quality is not None
                    else "ELRS serial link or RF telemetry is not available."
                ),
            ),
            ReadinessCheck(
                name="Flight controller telemetry",
                ready=readiness.flight_controller_telemetry
                and readiness.imu_available,
                detail="GPS, battery, or attitude telemetry is missing.",
            ),
            ReadinessCheck(
                name="GPS",
                ready=(readiness.gps_satellites or 0) >= 6,
                detail=(
                    f"{readiness.gps_satellites} satellites; minimum is 6."
                    if readiness.gps_satellites is not None
                    else "GPS satellite telemetry is unavailable."
                ),
            ),
            ReadinessCheck(
                name="Battery",
                ready=(readiness.battery_percent or 0) > 25,
                detail=(
                    f"{readiness.battery_percent:.1f}% remaining; must exceed 25%."
                    if readiness.battery_percent is not None
                    else "Battery telemetry is unavailable."
                ),
            ),
            ReadinessCheck(
                name="Companion temperature",
                ready=temperature is not None and temperature < 75,
                detail=(
                    f"{temperature:.1f} °C."
                    if temperature is not None
                    else "Temperature sensor is unavailable."
                ),
            ),
            ReadinessCheck(
                name="5.8 GHz video capture",
                ready=video_available,
                detail=(
                    "Capture device is available."
                    if video_available
                    else "Configured UVC capture device is unavailable."
                ),
            ),
        ]
        return HealthResponse(
            backend_online=True,
            elrs_configured=readiness.elrs_configured,
            elrs_connected=readiness.elrs_connected,
            elrs_link_quality=readiness.elrs_link_quality,
            flight_controller_telemetry=readiness.flight_controller_telemetry,
            gps_satellites=readiness.gps_satellites,
            battery_percent=readiness.battery_percent,
            imu_available=readiness.imu_available,
            companion_temperature_c=temperature,
            video_input_configured=self.video.configured,
            video_input_available=video_available,
            video_streaming=self.video.streaming,
            ready_for_flight=(
                readiness.ready_for_flight
                and video_available
                and all(check.ready for check in checks)
            ),
            checks=checks,
        )
