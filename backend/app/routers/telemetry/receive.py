from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.operations import EventLog
from app.schemas.telemetry import TelemetryData, MessageResponse
from app.utils.helper import generate_unique_id
from app.utils.redis import redis_client
import json

router = APIRouter()


@router.post("/receive", response_model=MessageResponse)
async def receive_telemetry(
    data: TelemetryData,
    db: AsyncSession = Depends(get_db)
):
    # Add timestamp if not present
    payload = data.dict()
    if not payload.get("timestamp"):
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Save latest telemetry in Redis
    await redis_client.set("telemetry:latest", json.dumps(payload, default=str))

    # Check for critical events
    if data.battery is not None and data.battery < 20:
        event = EventLog(
            id=generate_unique_id(),
            event_type="low_battery",
            severity="critical",
            message=f"Battery low: {data.battery}%",
            value=data.battery
        )
        db.add(event)

    if data.rain is True:
        event = EventLog(
            id=generate_unique_id(),
            event_type="rain_detected",
            severity="warning",
            message="Rain detected"
        )
        db.add(event)

    if data.lidar is not None and data.lidar < 1.0:
        event = EventLog(
            id=generate_unique_id(),
            event_type="obstacle_detected",
            severity="warning",
            message=f"Obstacle very close: {data.lidar}m",
            value=data.lidar
        )
        db.add(event)

    await db.commit()

    return {"message": "Telemetry received", "success": True}