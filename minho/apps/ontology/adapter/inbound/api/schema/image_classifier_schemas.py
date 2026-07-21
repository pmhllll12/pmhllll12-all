from __future__ import annotations

from pydantic import BaseModel


class LabelScoreSchema(BaseModel):
    label: str
    confidence: float


class ClassifyImageResponse(BaseModel):
    ok: bool
    label: str
    confidence: float
    top5: list[LabelScoreSchema]
    uncertain: bool
    inference_ms: float
    message: str = "classified"
