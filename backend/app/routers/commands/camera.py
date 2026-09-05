from fastapi import APIRouter, Depends
from app.db.models.account import User
from app.schemas.commands import MessageResponse
from app.core.security import get_current_user
from app.core.websocket import manager
from .flight import ensure_active_controller

router = APIRouter()


@router.post("/camera/start", response_model=MessageResponse)
async def camera_start(current_user: User = Depends(get_current_user)):
    await ensure_active_controller(current_user)
    await manager.send_to_drone({"type": "command", "command": "camera_start"})
    return {"message": "Camera started", "success": True}


@router.post("/camera/stop", response_model=MessageResponse)
async def camera_stop(current_user: User = Depends(get_current_user)):
    await ensure_active_controller(current_user)
    await manager.send_to_drone({"type": "command", "command": "camera_stop"})
    return {"message": "Camera stopped", "success": True}