from __future__ import annotations

from vision.adapter.outbound.resource_adapters.yolo.yolo_dataset_adapter import (
    YoloDatasetAdapter,
)
from vision.app.ports.input.face_training_use_case import FaceTrainingUseCase
from vision.app.ports.output.yolo_port import YoloDatasetPort
from vision.app.use_cases.yolo_interactor import YoloInteractor


def get_face_dataset_port() -> YoloDatasetPort:
    return YoloDatasetAdapter()


def get_face_training_use_case() -> FaceTrainingUseCase:
    return YoloInteractor(dataset_port=get_face_dataset_port())
