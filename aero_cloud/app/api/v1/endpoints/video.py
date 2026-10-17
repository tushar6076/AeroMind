from aiortc import RTCSessionDescription
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.api_auth import require_control_access
from app.schemas.video import WebRtcAnswer, WebRtcOffer
from app.services.video import VideoService

router = APIRouter(prefix="/video", tags=["video"])


@router.post(
    "/offer",
    response_model=WebRtcAnswer,
    dependencies=[Depends(require_control_access)],
)
async def create_video_answer(
    offer: WebRtcOffer,
    request: Request,
) -> WebRtcAnswer:
    service: VideoService = request.app.state.video_service
    try:
        answer = await service.create_answer(
            RTCSessionDescription(sdp=offer.sdp, type=offer.type)
        )
    except (OSError, RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    return WebRtcAnswer(sdp=answer.sdp, type=answer.type)
