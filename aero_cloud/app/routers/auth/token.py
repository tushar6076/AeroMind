from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.db.models.account import User
from app.schemas.auth import RefreshTokenRequest, VerifyTokenRequest, TokenResponse, MessageResponse
from app.core.security import create_access_token, verify_token
from app.utils.redis import get_refresh_token, set_refresh_token
from app.core.config import settings

router = APIRouter()


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    user_id = verify_token(data.refresh_token, expected_type="refresh")

    # Optional: Check if refresh token exists in Redis
    stored_token = await get_refresh_token(user_id)
    if not stored_token or stored_token != data.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(subject=user_id)

    return {
        "access_token": new_access_token,
        "refresh_token": data.refresh_token,
        "token_type": "bearer"
    }


@router.post("/token/verify", response_model=MessageResponse)
async def verify_access_token(data: VerifyTokenRequest):
    verify_token(data.token, expected_type="access")
    return {"message": "Token is valid"}