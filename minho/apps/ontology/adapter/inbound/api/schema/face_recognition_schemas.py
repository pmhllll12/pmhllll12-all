from __future__ import annotations

from pydantic import BaseModel


class PredictFaceResponse(BaseModel):
    ok: bool
    predicted_name: str
    confidence: float
    message: str = "predicted"
