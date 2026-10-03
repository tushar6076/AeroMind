from fastapi import APIRouter

from .flight import router as flight_router
from .manual import router as manual_router
from .camera import router as camera_router
from .extras import router as extras_router

router = APIRouter()

router.include_router(flight_router, tags=["Commands - Flight"])
router.include_router(manual_router, tags=["Commands - Manual"])
router.include_router(camera_router, tags=["Commands - Camera"])
router.include_router(extras_router, tags=["Commands - Extras"])