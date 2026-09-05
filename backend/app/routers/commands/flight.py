from fastapi import APIRouter, Depends, HTTPException, status
from app.db.models.account import User
from app.schemas.commands import MessageResponse
from app.core.security import get_current_user
from app.core.websocket import manager
from app.utils.redis import get_active_controller

router = APIRouter()


async def ensure_active_controller(current_user: User):
    active = await get_active_controller()
    if not active or active != current_user.id:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the active controller"
            )


@router.post("/takeoff", response_model=MessageResponse)
async def takeoff(current_user: User = Depends(get_current_user)):
    await ensure_active_controller(current_user)
    await manager.send_to_drone({
        "type": "command",
        "command": "takeoff"
    })
    return {"message": "Takeoff command sent", "success": True}


@router.post("/land", response_model=MessageResponse)
async def land(current_user: User = Depends(get_current_user)):
    await ensure_active_controller(current_user)
    await manager.send_to_drone({
        "type": "command",
        "command": "land"
    })
    return {"message": "Land command sent", "success": True}


@router.post("/rtl", response_model=MessageResponse)
async def rtl(current_user: User = Depends(get_current_user)):
    await ensure_active_controller(current_user)
    await manager.send_to_drone({
        "type": "command",
        "command": "rtl"
    })
    return {"message": "Return to Home command sent", "success": True}


@router.post("/hover", response_model=MessageResponse)
async def hover(current_user: User = Depends(get_current_user)):
    await ensure_active_controller(current_user)
    await manager.send_to_drone({
        "type": "command",
        "command": "hover"
    })
    return {"message": "Hover command sent", "success": True}


@router.post("/emergency-stop", response_model=MessageResponse)
async def emergency_stop(current_user: User = Depends(get_current_user)):
    await ensure_active_controller(current_user)
    await manager.send_to_drone({
        "type": "command",
        "command": "emergency_stop"
    })
    return {"message": "Emergency stop triggered", "success": True}