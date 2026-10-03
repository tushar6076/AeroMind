from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_db
from app.db.models.account import User, Device
from app.schemas.users import DeviceResponse, MessageResponse
from app.core.security import get_current_user

router = APIRouter()


@router.get("/devices", response_model=List[DeviceResponse])
async def get_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Device).where(Device.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Device).where(
            Device.user_id == current_user.id,
            Device.device_id == device_id
        )
    )
    device = result.scalars().first()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return device


@router.delete("/devices/{device_id}", response_model=MessageResponse)
async def remove_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Device).where(
            Device.user_id == current_user.id,
            Device.device_id == device_id
        )
    )
    device = result.scalars().first()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    await db.delete(device)
    await db.commit()

    return {"message": "Device removed successfully"}