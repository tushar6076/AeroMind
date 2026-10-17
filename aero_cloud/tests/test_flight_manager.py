import asyncio
import time
from types import SimpleNamespace

from app.core.config import settings
from app.schemas.flight import ControlInput
from app.services.flight.manager import FlightService


class RecordingBridge:
    connected = True

    def __init__(self) -> None:
        self.frames: list[dict[str, object]] = []

    async def send_controls(self, **controls: object) -> None:
        self.frames.append(controls)


def test_armed_control_loop_repeats_latest_stick_values(
    monkeypatch,
) -> None:
    async def exercise_control_loop() -> tuple[RecordingBridge, FlightService]:
        bridge = RecordingBridge()
        service = FlightService.__new__(FlightService)
        service._bridge = bridge
        service._session_active = True
        service._armed = True
        service._selected_mode = "acro"
        service._telemetry_listeners = set()
        service._publisher = None
        service._control_task = None
        service._control = ControlInput(roll=0.25, pitch=-0.5, yaw=0.1, throttle=0.4)
        service._control_lock = asyncio.Lock()
        service._last_control_at = time.monotonic()
        service.readiness = lambda _: SimpleNamespace(ready_for_flight=True)
        monkeypatch.setattr(
            "app.services.flight.manager.settings_temperature",
            lambda: 40.0,
        )
        monkeypatch.setattr(settings, "ELRS_ARM_CHANNEL", 5)

        task = asyncio.create_task(service._control_loop())
        service._control_task = task
        await asyncio.sleep(0.055)
        service._armed = False
        await service._stop_control_loop()
        return bridge, service

    bridge, service = asyncio.run(exercise_control_loop())

    assert len(bridge.frames) >= 2
    assert all(frame["roll"] == 0.25 for frame in bridge.frames)
    assert all(frame["pitch"] == -0.5 for frame in bridge.frames)
    assert all(frame["throttle"] == 0.4 for frame in bridge.frames)
    assert service._control_task is None


def test_control_loop_disarms_when_stick_heartbeat_expires(
    monkeypatch,
) -> None:
    async def exercise_expired_lease() -> tuple[RecordingBridge, FlightService]:
        bridge = RecordingBridge()
        service = FlightService.__new__(FlightService)
        service._bridge = bridge
        service._session_active = True
        service._armed = True
        service._selected_mode = "acro"
        service._telemetry_listeners = set()
        service._publisher = None
        service._control_task = None
        service._control = ControlInput(roll=0, pitch=0, yaw=0, throttle=0)
        service._control_lock = asyncio.Lock()
        service._last_control_at = time.monotonic() - 2
        service.readiness = lambda _: SimpleNamespace(ready_for_flight=True)
        monkeypatch.setattr(
            "app.services.flight.manager.settings_temperature",
            lambda: 40.0,
        )
        monkeypatch.setattr(settings, "ELRS_ARM_CHANNEL", 5)

        await service._control_loop()
        return bridge, service

    bridge, service = asyncio.run(exercise_expired_lease())

    assert len(bridge.frames) == 1
    assert bridge.frames[0]["armed"] is False
    assert service._armed is False
    assert service._session_active is False
