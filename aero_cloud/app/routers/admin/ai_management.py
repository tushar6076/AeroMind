from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.db.models.account import User
from app.db.models.intelligence import AIModel
from app.schemas.admin import MessageResponse
from app.core.security import get_current_admin
from app.utils.redis import (
    get_active_ai_model,
    list_active_ai_models,
    revoke_active_ai_model,
    revoke_all_ai_models,
)

router = APIRouter()


@router.patch("/ai/models/{model_id}/toggle", response_model=MessageResponse)
async def toggle_ai_model(
    model_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin-only: Force activate or deactivate a specific AI model."""
    result = await db.execute(select(AIModel).where(AIModel.id == model_id))
    model = result.scalars().first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="AI Model not found"
        )

    model.is_active = not model.is_active
    await db.commit()

    # If deactivated, revoke it from active in-play state in Redis as well
    if not model.is_active:
        await revoke_active_ai_model(model.key)

    state = "activated" if model.is_active else "deactivated"
    return {"message": f"AI model successfully {state}", "success": True}


# ==========================================
# In-Play Active Model Controls
# ==========================================

@router.get("/ai/models/in-play")
async def get_in_play_ai_models(
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """Admin-only: Show all AI models currently running/in play in Redis."""
    active_keys = await list_active_ai_models()
    
    in_play_models = []
    for key in active_keys:
        metadata = await get_active_ai_model(key)
        in_play_models.append({
            "model_key": key,
            "details": metadata
        })

    return {
        "success": True,
        "count": len(in_play_models),
        "in_play_models": in_play_models
    }


@router.post("/ai/models/{model_key}/revoke", response_model=MessageResponse)
async def force_revoke_ai_model(
    model_key: str,
    admin: User = Depends(get_current_admin)
):
    """Admin-only: Force-stop an active model key from in-play status in Redis."""
    active_data = await get_active_ai_model(model_key)
    if not active_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_key}' is not currently in play."
        )

    await revoke_active_ai_model(model_key)
    return {
        "message": f"Successfully revoked active model '{model_key}' from play.",
        "success": True
    }


@router.post("/ai/models/revoke-all", response_model=MessageResponse)
async def force_revoke_all_ai_models(
    admin: User = Depends(get_current_admin)
):
    """Admin-only: Emergency kill switch to clear all active models from Redis."""
    await revoke_all_ai_models()
    return {
        "message": "Successfully revoked all in-play AI models.",
        "success": True
    }