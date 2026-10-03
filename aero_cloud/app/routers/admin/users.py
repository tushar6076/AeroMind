from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_db
from app.db.models.account import User, AdminLog
from app.schemas.admin import AdminUserResponse, MessageResponse
from app.core.security import get_current_admin
from app.services.email.sender import send_approval_result_email
from app.utils.helper import generate_unique_id

router = APIRouter()


@router.get("/users", response_model=List[AdminUserResponse])
async def get_all_users(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/users/pending", response_model=List[AdminUserResponse])
async def get_pending_users(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.is_approved == False))
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users/{user_id}/approve", response_model=MessageResponse)
async def approve_user(
    user_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_approved = True
    await db.commit()

    # Log action
    log = AdminLog(
        id=generate_unique_id(),
        admin_id=admin.id,
        action="approve_user",
        target_type="user",
        target_id=user.id,
        details=f"Approved user {user.email}"
    )
    db.add(log)
    await db.commit()

    await send_approval_result_email(
        email=user.email,
        username=user.full_name or "User",
        status="Approved",
        message="You can now access all features of AeroMind."
    )

    return {"message": "User approved successfully"}


@router.post("/users/{user_id}/reject", response_model=MessageResponse)
async def reject_user(
    user_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_approved = False
    await db.commit()

    log = AdminLog(
        id=generate_unique_id(),
        admin_id=admin.id,
        action="reject_user",
        target_type="user",
        target_id=user.id,
        details=f"Rejected user {user.email}"
    )
    db.add(log)
    await db.commit()

    await send_approval_result_email(
        email=user.email,
        username=user.full_name or "User",
        status="Rejected",
        message="Your account request has been rejected by the admin."
    )

    return {"message": "User rejected successfully"}


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"message": "User deleted successfully"}