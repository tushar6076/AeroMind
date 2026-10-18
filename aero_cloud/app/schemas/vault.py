from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class VaultItem(BaseModel):
    id: str
    title: str
    media_type: Literal["image", "video"]
    captured_at: datetime | None
    duration_seconds: int | None
    size_bytes: int | None


class VaultInventory(BaseModel):
    mode: Literal["demo"]
    note: str
    items: list[VaultItem]
