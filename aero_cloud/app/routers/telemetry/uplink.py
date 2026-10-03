from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.websocket import manager

router = APIRouter()


@router.websocket("/uplink/{client_id}")
async def uplink_websocket(
    websocket: WebSocket,
    client_id: str,
    is_drone: bool = Query(False)
):
    """
    Uplink WebSocket connection.

    - App connects as:   /telemetry/uplink/{user_id}
    - Drone connects as: /telemetry/uplink/drone?is_drone=true

    Mainly used for:
    - App → Drone audio
    - App → Drone WebRTC signaling
    - App → Drone general messages
    - Drone → App responses
    """
    await manager.connect(client_id=client_id, websocket=websocket, is_drone=is_drone)

    try:
        while True:
            data = await websocket.receive_json()

            # From Drone → send to the active streaming user
            if is_drone:
                target_user = manager.get_active_stream_user()
                if target_user:
                    await manager.send_personal_message(data, user_id=target_user)

            # From App → send to Drone
            else:
                msg_type = data.get("type")

                if msg_type in ["webrtc_offer", "webrtc_ice", "webrtc_end", "audio"]:
                    await manager.send_to_drone(data)
                else:
                    # Forward any other message to drone
                    await manager.send_to_drone(data)

    except WebSocketDisconnect:
        manager.disconnect(client_id=client_id, is_drone=is_drone)