from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging

# Import DB Base and Engine
from app.db.base import Base
from app.db.session import engine

# Import Models so SQLAlchemy registers them before table creation
import app.db.models  # noqa: F401

# Setup logging
setup_logging()

# Import routers
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.admin import router as admin_router
from app.routers.connection import router as connection_router
from app.routers.commands import router as commands_router
from app.routers.telemetry import router as telemetry_router
from app.routers.ai import router as ai_router


def create_app() -> FastAPI:
    """Factory to create the AeroMind FastAPI application."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Automatically create missing tables on server boot
    @app.on_event("startup")
    async def on_startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Register Routers
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(users_router, prefix="/users", tags=["Users"])
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])
    app.include_router(connection_router, prefix="/connection", tags=["Connection"])
    app.include_router(commands_router, prefix="/commands", tags=["Commands"])
    app.include_router(telemetry_router, prefix="/telemetry", tags=["Telemetry"])
    app.include_router(ai_router, prefix="/ai", tags=["AI"])

    @app.get("/")
    async def root():
        return {
            "status": "AeroMind Backend Online",
            "environment": settings.ENVIRONMENT,
            "docs": "/docs"
        }

    return app


app = create_app()