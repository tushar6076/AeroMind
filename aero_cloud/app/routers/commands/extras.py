from fastapi import APIRouter, Depends
from app.db.models.account import User
from app.schemas.commands import MessageResponse
from app.core.security import get_current_user
from app.core.websocket import manager
from .flight import ensure_active_controller

router = APIRouter()


@router.post("/lights", response_model=MessageResponse)
async def toggle_lights(current_user: User = Depends(get_current_user)):
    await ensure_active_controller(current_user)
    await manager.send_to_drone({"type": "command", "command": "lights_toggle"})
    return {"message": "Lights toggled", "success": True}