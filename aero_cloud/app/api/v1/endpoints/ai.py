from fastapi import APIRouter

from app.schemas.ai import AIInventory
from app.services.ai.manager import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/loadout", response_model=AIInventory)
async def get_ai_loadout() -> AIInventory:
    return AIService().inventory()
