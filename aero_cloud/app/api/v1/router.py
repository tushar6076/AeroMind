from fastapi import APIRouter

from app.api.v1.endpoints import flight, system, telemetry, video

router = APIRouter()
router.include_router(system.router)
router.include_router(flight.router)
router.include_router(telemetry.router)
router.include_router(video.router)