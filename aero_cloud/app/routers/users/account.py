from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.account import User
from app.schemas.users import ChangePasswordRequest, MessageResponse
from app.core.security import get_current_user, verify_password, get_password_hash
from app.utils.redis import delete_refresh_token
from app.services.email.sender import send_delete_account_email

router = APIRouter()


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    current_user.hashed_password = get_password_hash(data.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    await delete_refresh_token(current_user.id)
    return {"message": "Logged out successfully"}


@router.delete("/delete-account", response_model=MessageResponse)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    email = current_user.email
    username = current_user.full_name or "User"

    await db.delete(current_user)
    await db.commit()

    await delete_refresh_token(current_user.id)
    await send_delete_account_email(email=email, username=username)

    return {"message": "Account deleted successfully"}