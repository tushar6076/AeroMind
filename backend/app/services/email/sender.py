from app.core.config import settings
from .templates import (
    WELCOME_HTML,
    OTP_HTML,
    LOGIN_ALERT_HTML,
    RESET_SUCCESS_HTML,
    DELETE_ACCOUNT_HTML,
    NEW_USER_REQUEST_HTML,
    APPROVAL_RESULT_HTML
)

from . import send_email

# ======================
# Email Functions
# ======================

async def send_welcome_email(email: str, username: str):
    html = WELCOME_HTML.format(username=username)
    await send_email("Welcome to AeroMind", [email], html)


async def send_otp_email(email: str, username: str, code: str):
    html = OTP_HTML.format(username=username, code=code)
    await send_email(f"{code} is your AeroMind code", [email], html)


async def send_login_alert(email: str, username: str, time: str):
    html = LOGIN_ALERT_HTML.format(username=username, time=time)
    await send_email("Security Alert: New Login Detected", [email], html)


async def send_reset_success_email(email: str, username: str):
    html = RESET_SUCCESS_HTML.format(username=username)
    await send_email("Password Reset Successful", [email], html)


async def send_delete_account_email(email: str, username: str):
    html = DELETE_ACCOUNT_HTML.format(username=username)
    await send_email("Account Deleted", [email], html)


async def send_approval_result_email(email: str, username: str, status: str, message: str = ""):
    html = APPROVAL_RESULT_HTML.format(
        username=username,
        status=status,
        message=message
    )
    await send_email(f"Account {status} - AeroMind", [email], html)


async def send_new_user_request_email(username: str, email: str):
    html = NEW_USER_REQUEST_HTML.format(username=username, email=email)
    await send_email(
        subject="New User Access Request - AeroMind",
        recipients=[settings.ADMIN_EMAIL],
        html=html
    )