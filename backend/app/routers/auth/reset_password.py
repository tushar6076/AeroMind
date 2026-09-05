from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.db.models.account import User
from app.schemas.auth import ResetPasswordRequest, MessageResponse
from app.core.security import get_password_hash
from app.utils.redis import get_otp, delete_otp
from app.services.email.sender import send_reset_success_email

router = APIRouter()


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Double-check OTP for safety
    stored_otp = await get_otp(data.email)
    if not stored_otp or stored_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(data.new_password)
    await db.commit()

    await delete_otp(data.email)
    await send_reset_success_email(
        email=user.email,
        username=user.full_name or "User"
    )

    return {"message": "Password reset successful"}