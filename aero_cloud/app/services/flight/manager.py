import asyncio
import logging
import time
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings
from app.schemas.flight import ControlInput, FlightModeName
from app.schemas.telemetry import TelemetrySnapshot
from app.services.flight.crsf import CrsfSerialBridge

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Readiness:
    elrs_configured: bool
    elrs_connected: bool
    elrs_link_quality: int | None
    flight_controller_telemetry: bool
    gps_satellites: int | None
    battery_percent: float | None
    imu_available: bool
    ready_for_flight: bool


class FlightService:
    def __init__(self) -> None:
        self._bridge = (
            CrsfSerialBridge(settings.ELRS_SERIAL_PORT, settings.ELRS_BAUD_RATE)
            if settings.ELRS_SERIAL_PORT
            else None
        )
        self._session_active = False
        self._armed = False
        self._selected_mode: FlightModeName | None = None
        self._telemetry_listeners: set[asyncio.Queue[TelemetrySnapshot]] = set()
        self._publisher: asyncio.Task[None] | None = None
        self._control_task: asyncio.Task[None] | None = None
        self._control = ControlInput(roll=0, pitch=0, yaw=0, throttle=0)
        self._control_lock = asyncio.Lock()
        self._last_control_at = 0.0

    async def start(self) -> None:
        if self._bridge is not None:
            try:
                await self._bridge.connect()
            except (OSError, ValueError) as error:
                self._bridge.last_error = str(error)
                logger.warning("Could not open ELRS CRSF bridge: %s", error)
        self._publisher = asyncio.create_task(self._publish_loop())

    async def close(self) -> None:
        try:
            await self.disarm()
        except RuntimeError as error:
            logger.error("Could not confirm ELRS disarm during shutdown: %s", error)
        self._session_active = False
        if self._publisher is not None:
            self._publisher.cancel()
            try:
                await self._publisher
            except asyncio.CancelledError:
                pass
            self._publisher = None
        if self._bridge is not None:
            await self._bridge.close()

    def current_telemetry(self) -> TelemetrySnapshot:
        if self._bridge is None:
            return TelemetrySnapshot(timestamp=time.time())
        telemetry = self._bridge.telemetry
        fresh = time.time() - telemetry.received_at < 3
        return TelemetrySnapshot(
            timestamp=telemetry.received_at or time.time(),
            link_quality=telemetry.link_quality if fresh else None,
            battery_voltage=telemetry.battery_voltage if fresh else None,
            battery_percent=telemetry.battery_percent if fresh else None,
            gps_latitude=telemetry.latitude if fresh else None,
            gps_longitude=telemetry.longitude if fresh else None,
            gps_satellites=telemetry.satellites if fresh else None,
            roll_degrees=telemetry.roll_degrees if fresh else None,
            pitch_degrees=telemetry.pitch_degrees if fresh else None,
            yaw_degrees=telemetry.yaw_degrees if fresh else None,
        )

    def readiness(self, temperature_c: float | None) -> Readiness:
        telemetry = self.current_telemetry()
        connected = self._bridge is not None and self._bridge.connected
        link_ok = connected and telemetry.link_quality is not None
        fc_telemetry = (
            telemetry.gps_satellites is not None
            and telemetry.battery_percent is not None
        )
        imu_available = telemetry.roll_degrees is not None
        ready = (
            link_ok
            and telemetry.link_quality is not None
            and telemetry.link_quality > 0
            and fc_telemetry
            and (telemetry.gps_satellites or 0) >= 6
            and (telemetry.battery_percent or 0) > 25
            and imu_available
            and temperature_c is not None
            and temperature_c < 75
        )
        return Readiness(
            elrs_configured=self._bridge is not None,
            elrs_connected=connected,
            elrs_link_quality=telemetry.link_quality,
            flight_controller_telemetry=fc_telemetry,
            gps_satellites=telemetry.gps_satellites,
            battery_percent=telemetry.battery_percent,
            imu_available=imu_available,
            ready_for_flight=bool(ready),
        )

    def set_mode(self, mode: FlightModeName) -> None:
        self._selected_mode = mode

    def status(self, temperature_c: float | None) -> dict:
        ready = self.readiness(temperature_c)
        bridge_error = self._bridge.last_error if self._bridge else None
        detail = (
            "Flight systems pass the configured readiness checks."
            if ready.ready_for_flight
            else bridge_error
            or "Hardware telemetry or one or more pre-flight checks are unavailable."
        )
        return {
            "session_active": self._session_active,
            "armed": self._armed,
            "arming_available": (
                settings.ELRS_ARM_CHANNEL is not None and self._bridge is not None
            ),
            "selected_mode": self._selected_mode,
            "control_available": (
                ready.ready_for_flight and self._session_active and self._armed
            ),
            "ready_for_flight": ready.ready_for_flight,
            "detail": detail,
        }

    def start_session(self, temperature_c: float | None) -> None:
        if not self.readiness(temperature_c).ready_for_flight:
            raise RuntimeError("Flight readiness checks have not passed")
        if self._selected_mode is None:
            raise RuntimeError("Select a flight mode before starting a session")
        self._session_active = True

    async def arm(self, temperature_c: float | None) -> None:
        if not self._session_active or not self.readiness(
            temperature_c
        ).ready_for_flight:
            raise RuntimeError("Flight session or readiness checks are not active")
        if self._selected_mode is None:
            raise RuntimeError("Select a flight mode before arming")
        if settings.ELRS_ARM_CHANNEL is None:
            raise RuntimeError("ELRS_ARM_CHANNEL must be configured before arming")
        await self._send_control_frame(
            ControlInput(roll=0, pitch=0, yaw=0, throttle=0),
            armed=True,
        )
        self._armed = True
        self._control = ControlInput(roll=0, pitch=0, yaw=0, throttle=0)
        self._last_control_at = time.monotonic()
        self._control_task = asyncio.create_task(self._control_loop())

    async def disarm(self) -> None:
        if not self._armed:
            return
        self._armed = False
        await self._stop_control_loop()
        if self._bridge is None or not self._bridge.connected:
            raise RuntimeError("ELRS link unavailable; disarm command was not sent")
        await self._send_control_frame(
            ControlInput(roll=0, pitch=0, yaw=0, throttle=0),
            armed=False,
        )
        self._control = ControlInput(roll=0, pitch=0, yaw=0, throttle=0)

    async def end_session(self) -> None:
        try:
            await self.disarm()
        finally:
            self._session_active = False

    async def send_control(self, control: ControlInput) -> None:
        if not self._session_active or not self._armed:
            raise RuntimeError("An active, armed flight session is required")
        if not self.readiness(settings_temperature()).ready_for_flight:
            await self.disarm()
            raise RuntimeError("Flight readiness was lost; transmitter disarmed")
        self._control = control
        self._last_control_at = time.monotonic()

    async def _control_loop(self) -> None:
        try:
            while self._armed:
                if not self._session_active or not self.readiness(
                    settings_temperature()
                ).ready_for_flight:
                    self._session_active = False
                    await self.disarm()
                    logger.warning(
                        "Flight readiness was lost; the transmitter was disarmed"
                    )
                    return
                if time.monotonic() - self._last_control_at > 1.0:
                    self._session_active = False
                    await self.disarm()
                    logger.warning(
                        "Flight control input expired; the transmitter was disarmed"
                    )
                    return
                await self._send_control_frame(self._control, armed=True)
                await asyncio.sleep(0.02)
        except asyncio.CancelledError:
            raise
        except RuntimeError as error:
            self._armed = False
            self._session_active = False
            logger.error("CRSF control stream stopped: %s", error)
        finally:
            if self._control_task is asyncio.current_task():
                self._control_task = None

    async def _stop_control_loop(self) -> None:
        task = self._control_task
        self._control_task = None
        if task is None or task is asyncio.current_task():
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    async def _send_control_frame(
        self,
        control: ControlInput,
        *,
        armed: bool,
    ) -> None:
        if self._bridge is None:
            raise RuntimeError("ELRS transmitter is not configured")
        if not self._bridge.connected:
            raise RuntimeError("ELRS CRSF serial bridge is not connected")
        channel = settings.ELRS_ARM_CHANNEL
        if channel is None:
            raise RuntimeError("ELRS_ARM_CHANNEL must be configured before control")
        async with self._control_lock:
            await self._bridge.send_controls(
                roll=control.roll,
                pitch=control.pitch,
                yaw=control.yaw,
                throttle=control.throttle,
                arm_channel=channel,
                arm_value=settings.ELRS_ARMED_CHANNEL_VALUE,
                disarm_value=172,
                armed=armed,
            )

    async def _publish_loop(self) -> None:
        while True:
            await asyncio.sleep(0.1)
            snapshot = self.current_telemetry()
            for listener in tuple(self._telemetry_listeners):
                if listener.full():
                    listener.get_nowait()
                await listener.put(snapshot)

    def subscribe(self) -> asyncio.Queue[TelemetrySnapshot]:
        queue: asyncio.Queue[TelemetrySnapshot] = asyncio.Queue(maxsize=1)
        self._telemetry_listeners.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[TelemetrySnapshot]) -> None:
        self._telemetry_listeners.discard(queue)


def settings_temperature() -> float | None:
    try:
        raw = Path(settings.HOST_THERMAL_PATH).read_text(encoding="ascii").strip()
    except OSError:
        return None
    try:
        return float(raw) / 1000
    except ValueError:
        return None