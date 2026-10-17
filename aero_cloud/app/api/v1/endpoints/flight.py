import asyncio
import base64
import binascii
import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.core.api_auth import require_control_access
from app.core.config import settings
from app.schemas.flight import ControlInput, FlightModeSelection, FlightStatus
from app.services.flight.manager import FlightService

router = APIRouter(prefix="/flight", tags=["flight"])
logger = logging.getLogger(__name__)


def _service(request: Request | WebSocket) -> FlightService:
    return request.app.state.flight_service


def _temperature(request: Request | WebSocket) -> float | None:
    return request.app.state.system_service.status().companion_temperature_c


@router.get("/status", response_model=FlightStatus)
async def get_flight_status(request: Request) -> FlightStatus:
    return _service(request).status(_temperature(request))


@router.post(
    "/mode",
    response_model=FlightStatus,
    dependencies=[Depends(require_control_access)],
)
async def select_flight_mode(
    selection: FlightModeSelection,
    request: Request,
) -> FlightStatus:
    service = _service(request)
    service.set_mode(selection.mode)
    return service.status(_temperature(request))


@router.post(
    "/session",
    response_model=FlightStatus,
    dependencies=[Depends(require_control_access)],
)
async def start_flight_session(request: Request) -> FlightStatus:
    service = _service(request)
    health = request.app.state.system_service.health()
    if not health.ready_for_flight:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Flight readiness checks have not passed.",
                "checks": [check.model_dump() for check in health.checks],
            },
        )
    try:
        service.start_session(health.companion_temperature_c)
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error
    return service.status(health.companion_temperature_c)


@router.delete(
    "/session",
    response_model=FlightStatus,
    dependencies=[Depends(require_control_access)],
)
async def end_flight_session(request: Request) -> FlightStatus:
    service = _service(request)
    try:
        await service.end_session()
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)
        ) from error
    return service.status(_temperature(request))


@router.post(
    "/arm",
    response_model=FlightStatus,
    dependencies=[Depends(require_control_access)],
)
async def arm_transmitter(request: Request) -> FlightStatus:
    service = _service(request)
    try:
        await service.arm(_temperature(request))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error
    return service.status(_temperature(request))


@router.post(
    "/disarm",
    response_model=FlightStatus,
    dependencies=[Depends(require_control_access)],
)
async def disarm_transmitter(request: Request) -> FlightStatus:
    service = _service(request)
    try:
        await service.disarm()
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)
        ) from error
    return service.status(_temperature(request))


@router.post(
    "/control",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_control_access)],
)
async def send_control(control: ControlInput, request: Request) -> None:
    try:
        await _service(request).send_control(control)
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error


@router.websocket("/control/ws")
async def control_stream(websocket: WebSocket) -> None:
    offered = websocket.scope.get("subprotocols", [])
    auth_protocol = next(
        (
            protocol.removeprefix("aeromind-auth-")
            for protocol in offered
            if protocol.startswith("aeromind-auth-")
        ),
        None,
    )
    try:
        token = (
            base64.urlsafe_b64decode(
                auth_protocol + "=" * (-len(auth_protocol) % 4)
            ).decode("utf-8")
            if auth_protocol is not None
            else None
        )
    except (binascii.Error, UnicodeDecodeError):
        token = None

    if (
        settings.API_ACCESS_TOKEN is None
        or token is None
        or not secrets.compare_digest(token, settings.API_ACCESS_TOKEN)
    ):
        await websocket.close(code=4401, reason="Invalid or missing access token")
        return

    await websocket.accept(subprotocol="aeromind-control")
    service = _service(websocket)
    try:
        while True:
            try:
                payload = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=1.0,
                )
            except TimeoutError:
                await websocket.close(code=4408, reason="Control heartbeat expired")
                return
            try:
                control = ControlInput.model_validate(payload)
                await service.send_control(control)
            except ValidationError:
                await websocket.close(code=1008, reason="Invalid control input")
                return
            except RuntimeError as error:
                await websocket.send_json({"error": str(error)})
                await websocket.close(code=4409, reason="Flight control unavailable")
                return
    except WebSocketDisconnect:
        pass
    finally:
        if service.status(_temperature(websocket))["armed"]:
            try:
                await service.end_session()
            except RuntimeError as error:
                logger.error(
                    "Could not disarm after control socket closed: %s", error
                )