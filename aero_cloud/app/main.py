from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import settings
from app.services.flight.manager import FlightService
from app.services.system import SystemService
from app.services.video import VideoService


def create_app() -> FastAPI:
    flight_service = FlightService()
    video_service = VideoService(
        device=settings.VIDEO_INPUT_DEVICE,
        width=settings.VIDEO_WIDTH,
        height=settings.VIDEO_HEIGHT,
        frame_rate=settings.VIDEO_FRAME_RATE,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.flight_service = flight_service
        app.state.video_service = video_service
        app.state.system_service = SystemService(flight_service, video_service)
        await flight_service.start()
        try:
            yield
        finally:
            await video_service.close()
            await flight_service.close()

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
