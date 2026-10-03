from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_db
from app.db.models.intelligence import AIModel
from app.schemas.ai import AIModelInfo

router = APIRouter()


# ==========================================
# Active Models (User-facing)
# ==========================================

@router.get("/models/active", response_model=List[AIModelInfo])
async def list_active_models(db: AsyncSession = Depends(get_db)):
    """Fetch all currently active models available for inference."""
    result = await db.execute(
        select(AIModel).where(AIModel.is_active == True)
    )
    return result.scalars().all()


@router.get("/models/active/{key}", response_model=AIModelInfo)
async def get_active_model_by_key(key: str, db: AsyncSession = Depends(get_db)):
    """Fetch specific active model details by key."""
    result = await db.execute(
        select(AIModel).where(AIModel.key == key, AIModel.is_active == True)
    )
    model = result.scalars().first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Active model '{key}' not found"
        )

    return model


# ==========================================
# General Model Queries (Admin / Comprehensive)
# ==========================================

@router.get("/models", response_model=List[AIModelInfo])
async def list_all_models(db: AsyncSession = Depends(get_db)):
    """List all models regardless of active state."""
    result = await db.execute(select(AIModel))
    return result.scalars().all()


@router.get("/models/{key}", response_model=AIModelInfo)
async def get_model_by_key(key: str, db: AsyncSession = Depends(get_db)):
    """List any model by key regardless of active state."""
    result = await db.execute(
        select(AIModel).where(AIModel.key == key)
    )
    model = result.scalars().first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Model '{key}' not found"
        )

    return model