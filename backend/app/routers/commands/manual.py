from fastapi import APIRouter, Depends
from app.db.models.account import User
from app.schemas.commands import JoystickLeftRequest, JoystickRightRequest, MessageResponse
from app.core.security import get_current_user
from app.core.websocket import manager
from .flight import ensure_active_controller

router = APIRouter()


@router.post("/joystick/left", response_model=MessageResponse)
async def joystick_left(
    data: JoystickLeftRequest,
    current_user: User = Depends(get_current_user)
):
    await ensure_active_controller(current_user)
    await manager.send_to_drone({
        "type": "command",
        "command": "joystick_left",
        "data": data.dict()
    })
    return {"message": "Left joystick command sent", "success": True}


@router.post("/joystick/right", response_model=MessageResponse)
async def joystick_right(
    data: JoystickRightRequest,
    current_user: User = Depends(get_current_user)
):
    await ensure_active_controller(current_user)
    await manager.send_to_drone({
        "type": "command",
        "command": "joystick_right",
        "data": data.dict()
    })
    return {"message": "Right joystick command sent", "success": True}