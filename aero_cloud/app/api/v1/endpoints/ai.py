from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.concurrency import run_in_threadpool

from app.core.api_auth import require_control_access
from app.core.config import settings
from app.schemas.ai import AIInferenceResult, AIInventory
from app.services.ai.manager import (
    AIImageError,
    AIInferenceUnavailable,
    AIService,
)

router = APIRouter(prefix="/ai", tags=["ai"])


def _service(request: Request) -> AIService:
    return request.app.state.ai_service


@router.get("/loadout", response_model=AIInventory)
async def get_ai_loadout(request: Request) -> AIInventory:
    return _service(request).inventory()


@router.post(
    "/infer",
    response_model=AIInferenceResult,
    dependencies=[Depends(require_control_access)],
)
async def infer_image(request: Request) -> AIInferenceResult:
    media_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    if media_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Send a JPEG, PNG, or WebP image as the raw request body.",
        )

    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > settings.AI_MAX_IMAGE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Image exceeds the configured upload size limit.",
                )
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Content-Length header.",
            ) from error

    image_bytes = bytearray()
    async for chunk in request.stream():
        image_bytes.extend(chunk)
        if len(image_bytes) > settings.AI_MAX_IMAGE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image exceeds the configured upload size limit.",
            )
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Image request body cannot be empty.",
        )

    try:
        return await run_in_threadpool(
            _service(request).infer,
            bytes(image_bytes),
            media_type,
        )
    except AIImageError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    except AIInferenceUnavailable as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
