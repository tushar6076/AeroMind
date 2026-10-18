from fastapi import APIRouter

from app.api.v1.endpoints import ai, flight, system, telemetry, vault, video

router = APIRouter()
router.include_router(system.router)
router.include_router(flight.router)
router.include_router(telemetry.router)
router.include_router(video.router)
router.include_router(ai.router)
router.include_router(vault.router)