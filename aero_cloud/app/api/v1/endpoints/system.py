from fastapi import APIRouter, Request

from app.schemas.system import HealthResponse, SystemStatus
from app.services.system import SystemService

router = APIRouter(prefix="/system", tags=["system"])


def _service(request: Request) -> SystemService:
    return request.app.state.system_service


@router.get("/status", response_model=SystemStatus)
async def get_system_status(request: Request) -> SystemStatus:
    return _service(request).status()


@router.get("/health", response_model=HealthResponse)
async def get_system_health(request: Request) -> HealthResponse:
    return _service(request).health()