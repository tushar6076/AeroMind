import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.db.models.account import User
from app.schemas.auth import ForgotPasswordRequest, VerifyOtpRequest, MessageResponse
from app.utils.redis import set_otp, get_otp
from app.services.email.sender import send_otp_email

router = APIRouter()


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = str(random.randint(100000, 999999))
    await set_otp(email=data.email, code=otp, expire_seconds=600)

    await send_otp_email(
        email=data.email,
        username=user.full_name or "User",
        code=otp
    )

    return {"message": "OTP sent to registered email"}


@router.post("/verify-otp", response_model=MessageResponse)
async def verify_otp(data: VerifyOtpRequest):
    stored_otp = await get_otp(data.email)

    if not stored_otp or stored_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    return {"message": "OTP verified successfully"}