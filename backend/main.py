import uvicorn
from app.core.config import settings

def start_server():
    """
    Entry point for the Skillinex FastAPI server.
    Configured via .env settings for host, port, and debug mode.
    """
    uvicorn.run(
        "app:app",  # Points to the 'app' variable in app/__init__.py
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,  # True in development, False in production
        log_level="info",
        workers=settings.WORKERS_COUNT if not settings.DEBUG else 1
    )

if __name__ == "__main__":
    start_server()