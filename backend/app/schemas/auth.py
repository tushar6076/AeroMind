from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ========== Signup ==========
class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class SignupResponse(BaseModel):
    message: str
    email: EmailStr


# ========== Login ==========
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_id: str
    device_info: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ========== Forgot Password Flow ==========
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str = Field(..., min_length=6)


# ========== Token ==========
class RefreshTokenRequest(BaseModel):
    refresh_token: str


class VerifyTokenRequest(BaseModel):
    token: str


class MessageResponse(BaseModel):
    message: str