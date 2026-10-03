from fastapi import APIRouter

from .users import router as users_router
from .control import router as control_router
from .security import router as security_router
from .ai_management import router as ai_router

router = APIRouter()

router.include_router(users_router, tags=["Admin - Users"])
router.include_router(control_router, tags=["Admin - Control"])
router.include_router(security_router, tags=["Admin - Security"])
router.include_router(ai_router, tags=["Admin - AI"])