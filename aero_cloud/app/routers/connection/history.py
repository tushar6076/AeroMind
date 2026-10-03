from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_db
from app.db.models.account import User
from app.db.models.operations import Connection
from app.schemas.connection import ConnectionHistoryItem
from app.core.security import get_current_user

router = APIRouter()


@router.get("/history", response_model=List[ConnectionHistoryItem])
async def get_connection_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Connection)
        .where(Connection.user_id == current_user.id)
        .order_by(Connection.created_at.desc())
    )
    return result.scalars().all()