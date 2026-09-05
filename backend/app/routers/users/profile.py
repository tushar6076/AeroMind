from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.account import User
from app.schemas.users import UserProfile, UpdateProfileRequest
from app.core.security import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if data.full_name:
        current_user.full_name = data.full_name

    await db.commit()
    await db.refresh(current_user)
    return current_user