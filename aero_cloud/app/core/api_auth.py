import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


async def require_control_access(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    if settings.API_ACCESS_TOKEN is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Set API_ACCESS_TOKEN on the backend before enabling controls.",
        )
    if credentials is None or not secrets.compare_digest(
        credentials.credentials,
        settings.API_ACCESS_TOKEN,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing backend access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
