from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrainFaceRecognizerCommand:
    epochs: int = 50
    batch_size: int = 16
    image_size: int = 224


@dataclass(frozen=True)
class TrainFaceRecognizerResult:
    ok: bool
    weights_path: str
    epochs: int
    message: str = "trained"
