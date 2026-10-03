from fastapi import APIRouter, Depends
from app.db.models.account import User
from app.schemas.admin import MessageResponse, ForcedControlRequest
from app.core.security import get_current_admin
from app.utils.redis import set_active_controller, get_active_controller, clear_active_controller

router = APIRouter()


@router.get("/active-controller")
async def get_controller(admin: User = Depends(get_current_admin)):
    controller = await get_active_controller()
    return {"active_controller": controller}


@router.post("/forced-control", response_model=MessageResponse)
async def forced_control(
    data: ForcedControlRequest,
    admin: User = Depends(get_current_admin)
):
    await set_active_controller(admin.id)
    return {"message": "Forced control taken successfully"}


@router.post("/release-control", response_model=MessageResponse)
async def release_control(admin: User = Depends(get_current_admin)):
    await clear_active_controller()
    return {"message": "Control released successfully"}