from fastapi import APIRouter

from .models import router as models_router
from .identify import router as identify_router

router = APIRouter()

router.include_router(models_router, tags=["AI - Models"])
router.include_router(identify_router, tags=["AI - Identify"])