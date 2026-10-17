from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.flight.manager import FlightService

router = APIRouter(tags=["telemetry"])


@router.websocket("/telemetry/ws")
async def telemetry_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    service: FlightService = websocket.app.state.flight_service
    queue = service.subscribe()
    try:
        await websocket.send_json(
            {"type": "telemetry", "data": service.current_telemetry().model_dump()}
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