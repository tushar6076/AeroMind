from fastapi import APIRouter, HTTPException
from app.schemas.telemetry import TelemetryData
from app.utils.redis import redis_client
import json

router = APIRouter()


@router.get("/latest", response_model=TelemetryData)
async def get_latest_telemetry():
    """Fallback for global singleton telemetry"""
    data = await redis_client.get("telemetry:latest")
    if not data:
        raise HTTPException(status_code=404, detail="No telemetry data available")
    return json.loads(data)


@router.get("/latest/{drone_id}", response_model=TelemetryData)
async def get_drone_specific_telemetry(drone_id: str):
    """Fetch live telemetry for a specific drone or hardware ID via ELRS/USB link"""
    data = await redis_client.get(f"telemetry:drone:{drone_id}")

    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No telemetry data available for drone/session {drone_id}"
        )

    return json.loads(data)