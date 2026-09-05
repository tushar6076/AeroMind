from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from app.core.config import settings

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_email(subject: str, recipients: list, html: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=html,
        subtype=MessageType.html
    )
    fm = FastMail(mail_config)
    await fm.send_message(message)


from .sender import (
    send_welcome_email, send_otp_email, send_login_alert, 
    send_reset_success_email, send_delete_account_email, 
    send_approval_result_email
)

__all__ = [
    "send_welcome_email",
    "send_otp_email",
    "send_login_alert",
    "send_reset_success_email",
    "send_delete_account_email",
    "send_approval_result_email"
]