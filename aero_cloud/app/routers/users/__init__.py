from fastapi import APIRouter

from .profile import router as profile_router
from .account import router as account_router
from .devices import router as devices_router

router = APIRouter()

router.include_router(profile_router, tags=["Users"])
router.include_router(account_router, tags=["Users"])
router.include_router(devices_router, tags=["Users"])