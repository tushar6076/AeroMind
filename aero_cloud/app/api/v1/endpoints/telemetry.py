import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.services.flight.manager import FlightService

router = APIRouter(tags=["telemetry"])


@router.websocket("/telemetry/ws")
async def telemetry_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    service: FlightService = websocket.app.state.flight_service
    latest = await websocket.app.state.redis_store.load_telemetry()
    if (
        latest is not None
        and isinstance(latest.get("timestamp"), (int, float))
        and 0
        <= time.time() - latest["timestamp"]
        < settings.TELEMETRY_MAX_AGE_SECONDS
    ):
        initial_telemetry = latest
    else:
        initial_telemetry = service.current_telemetry().model_dump()
    queue = service.subscribe()
    try:
        await websocket.send_json(
            {"type": "telemetry", "data": initial_telemetry}
        )
        while True:
            telemetry = await queue.get()
            await websocket.send_json(
                {"type": "telemetry", "data": telemetry.model_dump()}
            )
    except WebSocketDisconnect:
        pass
    finally:
        service.unsubscribe(queue)