from typing import Literal

from pydantic import BaseModel, Field


class AIModelSummary(BaseModel):
    id: str
    name: str
    version: str
    task: str
    status: str
    stage_count: int


class AIInventory(BaseModel):
    mode: Literal["missions"]
    note: str
    router_status: str
    models: list[AIModelSummary]


class AIStagePrediction(BaseModel):
    stage_id: str
    stage_name: str
    task: str
    status: Literal["predicted", "skipped"]
    label: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class AIInferenceResult(BaseModel):
    mission_id: str
    mission_name: str
    router_label: str
    router_confidence: float = Field(ge=0.0, le=1.0)
    stages: list[AIStagePrediction]
