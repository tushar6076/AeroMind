import asyncio
import json

from app.core.config import settings
from app.services.redis import keys
from app.services.redis.store import RedisStore


class FakePipeline:
    def __init__(self, redis: "FakeRedis") -> None:
        self.redis = redis
        self.operations: list[tuple[str, str, str, int | None]] = []

    async def __aenter__(self) -> "FakePipeline":
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    def set(self, key: str, value: str, *, ex: int) -> None:
        self.operations.append(("set", key, value, ex))

    def publish(self, channel: str, value: str) -> None:
        self.operations.append(("publish", channel, value, None))

    async def execute(self) -> None:
        for operation, key, value, ttl in self.operations:
            if operation == "set":
                self.redis.values[key] = value
                self.redis.ttls[key] = ttl
            else:
                self.redis.published.append((key, value))


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int | None] = {}
        self.published: list[tuple[str, str]] = []

    async def ping(self) -> bool:
        return True

    def pipeline(self, *, transaction: bool) -> FakePipeline:
        assert transaction is False
        return FakePipeline(self)

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def set(self, key: str, value: str, *, ex: int) -> None:
        self.values[key] = value
        self.ttls[key] = ex

    async def aclose(self) -> None:
        return None


def _store_with_fake_redis() -> tuple[RedisStore, FakeRedis]:
    store = RedisStore.__new__(RedisStore)
    redis = FakeRedis()
    store._client = redis
    store._available = True
    store._next_retry_at = 0.0
    return store, redis


def test_telemetry_is_cached_with_ttl_and_published() -> None:
    async def exercise() -> tuple[dict[str, object] | None, FakeRedis]:
        store, redis = _store_with_fake_redis()
        telemetry = {"timestamp": 123.0, "link_quality": 91}

        await store.save_telemetry(telemetry)
        loaded = await store.load_telemetry()

        return loaded, redis

    loaded, redis = asyncio.run(exercise())

    assert loaded == {"timestamp": 123.0, "link_quality": 91}
    assert redis.ttls[keys.TELEMETRY_LATEST] == (
        settings.REDIS_TELEMETRY_TTL_SECONDS
    )
    assert redis.published == [
        (keys.TELEMETRY_CHANNEL, json.dumps(loaded, separators=(",", ":")))
    ]


def test_flight_state_is_cached_with_a_ttl() -> None:
    async def exercise() -> tuple[dict[str, object] | None, FakeRedis]:
        store, redis = _store_with_fake_redis()
        state = {
            "session_active": False,
            "armed": False,
            "selected_mode": "acro",
        }

        await store.save_flight_state(state)
        loaded = await store.load_flight_state()

        return loaded, redis

    loaded, redis = asyncio.run(exercise())

    assert loaded == {
        "session_active": False,
        "armed": False,
        "selected_mode": "acro",
    }
    assert redis.ttls[keys.FLIGHT_STATE] == settings.REDIS_FLIGHT_STATE_TTL_SECONDS


def test_flight_service_restores_only_a_valid_selected_mode() -> None:
    class StateStore:
        async def load_flight_state(self) -> dict[str, object]:
            return {
                "session_active": True,
                "armed": True,
                "selected_mode": "acro",
            }

    async def exercise() -> tuple[bool, bool, str | None]:
        from app.services.flight.manager import FlightService

        service = FlightService(StateStore())
        await service.restore_state()
        return service._session_active, service._armed, service._selected_mode

    session_active, armed, selected_mode = asyncio.run(exercise())

    assert session_active is False
    assert armed is False
    assert selected_mode == "acro"
