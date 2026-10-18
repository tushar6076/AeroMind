from typing import Literal

from pydantic import BaseModel


class AIModelSummary(BaseModel):
    name: str
    version: str
    task: str
    status: str


class AIInventory(BaseModel):
    mode: Literal["demo"]
    note: str
    models: list[AIModelSummary]
