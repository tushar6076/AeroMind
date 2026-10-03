import json
import redis.asyncio as redis
from typing import Any, Optional, List
from app.core.config import settings

# Initialize Redis
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


# ======================
# OTP Logic
# ======================
async def set_otp(email: str, code: str, expire_seconds: int = 600):
    await redis_client.set(f"otp:{email}", code, ex=expire_seconds)

async def get_otp(email: str):
    return await redis_client.get(f"otp:{email}")

async def delete_otp(email: str):
    await redis_client.delete(f"otp:{email}")


# ======================
# Auth Token Helpers
# ======================
async def set_refresh_token(user_id: str, token: str, expire_seconds: int):
    await redis_client.set(f"refresh:{user_id}", token, ex=expire_seconds)

async def get_refresh_token(user_id: str):
    return await redis_client.get(f"refresh:{user_id}")

async def delete_refresh_token(user_id: str):
    await redis_client.delete(f"refresh:{user_id}")


# ======================
# Flight / Connection Token Logic
# ======================
async def set_connection_token(connection_id: str, data: dict, expire_seconds: int = 3600):
    """
    Store active flight/connection session data
    """
    await redis_client.set(
        f"connection:{connection_id}",
        json.dumps(data),
        ex=expire_seconds
    )

async def get_connection_token(connection_id: str) -> Optional[dict]:
    raw = await redis_client.get(f"connection:{connection_id}")
    return json.loads(raw) if raw else None

async def delete_connection_token(connection_id: str):
    await redis_client.delete(f"connection:{connection_id}")


# ======================
# Active Controller Tracking
# ======================
async def set_active_controller(user_id: str, expire_seconds: int = 3600):
    await redis_client.set("active_controller", user_id, ex=expire_seconds)

async def get_active_controller() -> Optional[str]:
    return await redis_client.get("active_controller")

async def clear_active_controller():
    await redis_client.delete("active_controller")


# ======================
# Active AI Model Management ("In Play")
# ======================
async def set_active_ai_model(model_key: str, metadata: Optional[dict] = None, expire_seconds: Optional[int] = None):
    """
    Set an AI model as active/in-play.
    If metadata is provided, it will be JSON serialized.
    """
    value = json.dumps(metadata) if metadata else "active"
    if expire_seconds:
        await redis_client.set(f"ai:active_model:{model_key}", value, ex=expire_seconds)
    else:
        await redis_client.set(f"ai:active_model:{model_key}", value)


async def get_active_ai_model(model_key: str) -> Optional[Any]:
    """
    Check if a specific AI model is currently active/in-play.
    """
    raw = await redis_client.get(f"ai:active_model:{model_key}")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


async def revoke_active_ai_model(model_key: str):
    """
    Revoke/stop a model from being active.
    """
    await redis_client.delete(f"ai:active_model:{model_key}")


async def list_active_ai_models() -> List[str]:
    """
    List all model keys currently active in play.
    """
    keys = await redis_client.keys("ai:active_model:*")
    return [key.replace("ai:active_model:", "") for key in keys]


async def revoke_all_ai_models():
    """
    Emergency revoke of all active in-play models.
    """
    keys = await redis_client.keys("ai:active_model:*")
    if keys:
        await redis_client.delete(*keys)