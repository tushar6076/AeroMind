from fastapi import APIRouter

from .request import router as request_router
from .history import router as history_router

router = APIRouter()

router.include_router(request_router, tags=["Connection"])
router.include_router(history_router, tags=["Connection"])