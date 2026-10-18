from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import settings
from app.services.flight.manager import FlightService
from app.services.ai.manager import AIService
from app.services.redis.store import RedisStore
from app.services.system import SystemService
from app.services.video import VideoService


def create_app() -> FastAPI:
    redis_store = RedisStore()
    flight_service = FlightService(redis_store)
    video_service = VideoService(
        device=settings.VIDEO_INPUT_DEVICE,
        width=settings.VIDEO_WIDTH,
        height=settings.VIDEO_HEIGHT,
        frame_rate=settings.VIDEO_FRAME_RATE,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.redis_store = redis_store
        app.state.flight_service = flight_service
        app.state.video_service = video_service
        app.state.ai_service = AIService()
        app.state.system_service = SystemService(flight_service, video_service)
        await redis_store.start()
        try:
            await flight_service.restore_state()
            await flight_service.start()
            await flight_service.persist_state()
            yield
        finally:
            try:
                await video_service.close()
                await flight_service.close()
            finally:
                await redis_store.close()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        docs_url="/docs",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"status": "online", "service": settings.PROJECT_NAME}

    return app


app = create_app()
