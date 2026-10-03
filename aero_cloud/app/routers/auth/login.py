from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.db.models.account import User, Device
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.utils.helper import generate_unique_id
from app.utils.redis import set_refresh_token
from app.core.config import settings
from app.services.email.sender import send_login_alert

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 1. Find user
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email"
        )

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Please contact admin."
        )

    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not approved yet. Please wait for admin approval."
        )

    # 2. Handle Device Binding (Single Device Login)
    devices_result = await db.execute(
        select(Device).where(Device.user_id == user.id, Device.is_active == True)
    )
    active_devices = devices_result.scalars().all()

    for device in active_devices:
        if device.device_id != data.device_id:
            device.is_active = False

    device_result = await db.execute(
        select(Device).where(
            Device.user_id == user.id,
            Device.device_id == data.device_id
        )
    )
    current_device = device_result.scalars().first()

    # Fixed: Use naive UTC datetime matching PostgreSQL column types
    now_naive = datetime.utcnow()

    if current_device:
        current_device.is_active = True
        current_device.last_login = now_naive
        current_device.device_info = data.device_info
    else:
        new_device = Device(
            id=generate_unique_id(),
            user_id=user.id,
            device_id=data.device_id,
            device_info=data.device_info,
            is_active=True,
            last_login=now_naive
        )
        db.add(new_device)

    user.last_active = now_naive
    await db.commit()

    # 3. Generate Tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    # Handle Redis gracefully in case connection fails in dev
    try:
        await set_refresh_token(
            user_id=user.id,
            token=refresh_token,
            expire_seconds=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
    except Exception as e:
        print(f"[WARNING] Failed to set refresh token in Redis: {e}")

    # Handle Email dispatch gracefully
    try:
        await send_login_alert(
            email=user.email,
            username=user.full_name or "User",
            time=now_naive.strftime("%d %b %Y, %I:%M %p")
        )
    except Exception as e:
        print(f"[WARNING] Failed to send login alert email: {e}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }