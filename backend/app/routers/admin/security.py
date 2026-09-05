from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.db.models.account import User
from app.core.security import get_current_admin
from app.schemas.admin import MessageResponse

router = APIRouter()


class Admin2FARequest(BaseModel):
    code: str


@router.post("/verify-2fa", response_model=MessageResponse)
async def verify_2fa(
    data: Admin2FARequest,
    admin: User = Depends(get_current_admin)
):
    # Placeholder for real 2FA logic (can connect with Redis OTP later)
    if data.code != "123456":  # temporary
        raise HTTPException(status_code=400, detail="Invalid 2FA code")

    return {"message": "2FA verified successfully"}