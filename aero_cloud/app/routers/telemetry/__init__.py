from fastapi import APIRouter

from .receive import router as receive_router
from .latest import router as latest_router
from .stream import router as stream_router
from .uplink import router as uplink_router

router = APIRouter()

router.include_router(receive_router, tags=["Telemetry"])
router.include_router(latest_router, tags=["Telemetry"])
router.include_router(stream_router, tags=["Telemetry - Stream"])
router.include_router(uplink_router, tags=["Telemetry - Uplink"])