from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.db.models.account import User
from app.db.models.operations import Connection
from app.schemas.connection import ConnectionStatusResponse, MessageResponse
from app.core.security import get_current_user
from app.utils.helper import generate_unique_id
from app.utils.redis import (
    get_active_controller,
    set_active_controller,
    clear_active_controller
)

router = APIRouter()


@router.post("/request", response_model=MessageResponse)
async def request_connection(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    active_controller = await get_active_controller()

    if active_controller and active_controller != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Drone is already under control by another user"
        )

    # Set current user as active controller
    await set_active_controller(current_user.id)

    # Create connection record
    connection = Connection(
        id=generate_unique_id(),
        user_id=current_user.id,
        status="connected",
        is_active_controller=True,
        started_at=datetime.now(timezone.utc)
    )
    db.add(connection)
    await db.commit()

    return {"message": "Connected successfully. You are now the active controller."}


@router.get("/status", response_model=ConnectionStatusResponse)
async def connection_status(
    current_user: User = Depends(get_current_user)
):
    active_controller = await get_active_controller()

    is_active = active_controller == current_user.id if active_controller else False

    return {
        "is_connected": bool(active_controller),
        "is_active_controller": is_active,
        "active_controller_id": active_controller,
        "message": "You are the active controller" if is_active else (
            "Drone is under control by another user" if active_controller else "Drone is free"
        )
    }


@router.get("/is-busy")
async def is_busy(current_user: User = Depends(get_current_user)):
    active_controller = await get_active_controller()
    return {
        "is_busy": bool(active_controller),
        "active_controller_id": active_controller
    }


@router.post("/disconnect", response_model=MessageResponse)
async def disconnect(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    active_controller = await get_active_controller()

    if not active_controller:
        return {"message": "No active connection found"}

    if active_controller != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the active controller"
        )

    # Clear Redis
    await clear_active_controller()

    # Update latest connection record
    result = await db.execute(
        select(Connection)
        .where(
            Connection.user_id == current_user.id,
            Connection.is_active_controller == True
        )
        .order_by(Connection.created_at.desc())
    )
    connection = result.scalars().first()

    if connection:
        connection.status = "disconnected"
        connection.is_active_controller = False
        connection.ended_at = datetime.now(timezone.utc)
        await db.commit()

    return {"message": "Disconnected successfully"}