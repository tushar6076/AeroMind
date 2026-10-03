from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.db.models.account import User
from app.db.models.intelligence import AIModel, AIRequest
from app.schemas.ai import IdentifyRequest, IdentifyResponse
from app.core.security import get_current_user
from app.services.ai.identify import identify as run_identification
from app.utils.helper import generate_unique_id
from app.utils.redis import set_active_ai_model, revoke_active_ai_model

router = APIRouter()


@router.post("/identify", response_model=IdentifyResponse)
async def identify(
    data: IdentifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch model from DB and verify it is active
    result = await db.execute(
        select(AIModel).where(
            AIModel.key == data.application, 
            AIModel.is_active == True
        )
    )
    model = result.scalars().first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="AI application not found or inactive"
        )

    # 2. Log initial AI Request entry in Postgres
    ai_request = AIRequest(
        id=generate_unique_id(),
        user_id=current_user.id,
        model_id=model.id,
        application=data.application,
        level=str(data.level),
        input_data={"data": str(data.data)[:500]},  # Store truncated preview
        status="processing"
    )
    db.add(ai_request)
    await db.commit()
    await db.refresh(ai_request)

    # 3. Mark model as currently "in play" in Redis
    await set_active_ai_model(
        model_key=data.application,
        metadata={
            "request_id": ai_request.id,
            "user_id": current_user.id,
            "provider": data.preferred_provider or model.provider,
            "started_at": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # 4. Execute identification service
        result = await run_identification(
            input_data={
                "data": data.data,
                "level": data.level
            },
            application=data.application,
            preferred_provider=data.preferred_provider,
            enhance_with_llm=data.enhance
        )

        # 5. Update DB record on success
        ai_request.result = result.get("extra", {}).get("local_result", {})
        ai_request.enhanced_result = result.get("content")
        ai_request.status = "completed"
        ai_request.completed_at = datetime.now(timezone.utc)
        await db.commit()

        return {
            "success": True,
            "application": data.application,
            "level": data.level,
            "result": result.get("extra", {}).get("local_result", {}),
            "enhanced": result.get("content"),
            "provider": result.get("provider")
        }

    except Exception as e:
        # 6. Mark DB request record as failed
        ai_request.status = "failed"
        ai_request.result = {"error": str(e)}
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )

    finally:
        # 7. Always remove model from "in play" state in Redis when processing finishes
        await revoke_active_ai_model(data.application)