from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.db.models.account import User
from app.schemas.auth import SignupRequest, SignupResponse
from app.core.security import get_password_hash
from app.services.email.sender import send_welcome_email, send_new_user_request_email
from app.utils.helper import generate_unique_id

router = APIRouter()


@router.post("/signup", response_model=SignupResponse)
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    new_user = User(
        id=generate_unique_id(),
        full_name=data.full_name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        is_verified=False,
        is_approved=False,
        is_active=True,
        role="user"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Send emails
    await send_welcome_email(email=data.email, username=data.full_name)
    await send_new_user_request_email(username=data.full_name, email=data.email)

    return {
        "message": "Signup successful. Please wait for admin approval.",
        "email": data.email
    }