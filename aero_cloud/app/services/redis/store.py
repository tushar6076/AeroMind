import json
import logging
import time
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.services.redis import keys

logger = logging.getLogger(__name__)


class RedisStore:
    def __init__(self, url: str = settings.REDIS_URL) -> None:
        self._client: Redis = Redis.from_url(url, decode_responses=True)
        self._available = False
        self._next_retry_at = 0.0

    async def start(self) -> bool:
        if await self._connect():
            logger.info("Connected to Redis for short-lived application state")
            return True
        logger.warning("Redis is unavailable; short-lived state will not persist")
        return False

    async def _connect(self) -> bool:
        try:
            await self._client.ping()
        except RedisError:
            self._available = False
            self._next_retry_at = (
                time.monotonic() + settings.REDIS_RECONNECT_INTERVAL_SECONDS
            )
            return False
        was_retrying = self._next_retry_at != 0.0
        self._available = True
        self._next_retry_at = 0.0
        if was_retrying:
            logger.info("Redis connection restored")
        return True

    async def _ensure_available(self) -> bool:
        if self._available:
            return True
        if time.monotonic() < self._next_retry_at:
            return False
        return await self._connect()

    def _mark_unavailable(self, operation: str) -> None:
        if self._available:
            logger.warning("Redis became unavailable during %s", operation)
        self._available = False
        self._next_retry_at = (
            time.monotonic() + settings.REDIS_RECONNECT_INTERVAL_SECONDS
        )

    async def save_telemetry(self, telemetry: dict[str, Any]) -> None:
        if not await self._ensure_available():
            return
        payload = json.dumps(telemetry, separators=(",", ":"))
        try:
            async with self._client.pipeline(transaction=False) as pipeline:
                pipeline.set(
                    keys.TELEMETRY_LATEST,
                    payload,
                    ex=settings.REDIS_TELEMETRY_TTL_SECONDS,
                )
                pipeline.publish(keys.TELEMETRY_CHANNEL, payload)
                await pipeline.execute()
        except RedisError:
            self._mark_unavailable("telemetry persistence")

    async def load_telemetry(self) -> dict[str, Any] | None:
        if not await self._ensure_available():
            return None
        try:
            payload = await self._client.get(keys.TELEMETRY_LATEST)
        except RedisError:
            self._mark_unavailable("telemetry retrieval")
            return None
        if payload is None:
            return None
        try:
            result = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("Redis contains invalid JSON for latest telemetry")
            return None
        if not isinstance(result, dict):
            logger.error("Redis latest telemetry is not a JSON object")
            return None
        return result

    async def load_flight_state(self) -> dict[str, Any] | None:
        if not await self._ensure_available():
            return None
        try:
            payload = await self._client.get(keys.FLIGHT_STATE)
        except RedisError:
            self._mark_unavailable("flight-state retrieval")
            return None
        if payload is None:
            return None
        try:
            result = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("Redis contains invalid JSON for flight-session state")
            return None
        if not isinstance(result, dict):
            logger.error("Redis flight-session state is not a JSON object")
            return None
        return result

    async def save_flight_state(self, state: dict[str, Any]) -> None:
        if not await self._ensure_available():
            return
        payload = json.dumps(state, separators=(",", ":"))
        try:
            await self._client.set(
                keys.FLIGHT_STATE,
                payload,
                ex=settings.REDIS_FLIGHT_STATE_TTL_SECONDS,
            )
        except RedisError:
            self._mark_unavailable("flight-state persistence")

    async def close(self) -> None:
        await self._client.aclose()
