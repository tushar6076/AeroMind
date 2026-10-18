from fastapi import APIRouter

from app.schemas.vault import VaultInventory
from app.services.vault import VaultService

router = APIRouter(prefix="/vault", tags=["vault"])


@router.get("/items", response_model=VaultInventory)
async def get_vault_items() -> VaultInventory:
    return VaultService().inventory()
