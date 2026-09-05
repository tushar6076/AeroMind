from fastapi import APIRouter, Depends, HTTPException
from app.db.models.account import User
from app.core.security import get_current_user
from app.core.websocket import manager
from app.schemas.telemetry import SDPPayload, ICECandidatePayload ,MessageResponse

router = APIRouter()

@router.post("/stream/offer", response_model=MessageResponse)
async def handle_offer(
    data: SDPPayload,
    current_user: User = Depends(get_current_user)
):
    """
    App sends WebRTC offer → forward to drone
    """
    await manager.send_to_drone({
        "type": "webrtc_offer",
        "from": current_user.id,
        "sdp": data.sdp,
        "sdp_type": data.type
    })
    return {"message": "Offer sent to drone", "success": True}


@router.post("/stream/answer", response_model=MessageResponse)
async def handle_answer(
    data: SDPPayload,
    current_user: User = Depends(get_current_user)
):
    """
    Drone sends answer → forward to the app user
    """
    target_user = data.target
    if not target_user:
        raise HTTPException(status_code=400, detail="Target user required")

    await manager.send_personal_message({
        "type": "webrtc_answer",
        "sdp": data.sdp,
        "sdp_type": data.type
    }, user_id=target_user)

    return {"message": "Answer forwarded", "success": True}


@router.post("/stream/ice-candidate", response_model=MessageResponse)
async def handle_ice_candidate(
    data: ICECandidatePayload,
    current_user: User = Depends(get_current_user)
):
    """
    Exchange ICE candidates between App and Drone
    """
    payload = {
        "type": "webrtc_ice",
        "candidate": data.candidate,
        "from": current_user.id
    }

    if data.target == "drone":
        await manager.send_to_drone(payload)
    else:
        await manager.send_personal_message(payload, user_id=data.target)

    return {"message": "ICE candidate forwarded", "success": True}


@router.post("/stream/end", response_model=MessageResponse)
async def end_stream(current_user: User = Depends(get_current_user)):
    """
    Notify that streaming has ended
    """
    await manager.send_to_drone({
        "type": "webrtc_end",
        "from": current_user.id
    })
    return {"message": "Stream end signal sent", "success": True}