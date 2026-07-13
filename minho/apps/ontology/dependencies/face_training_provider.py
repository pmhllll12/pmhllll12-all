from __future__ import annotations

from ontology.adapter.outbound.resource_adapters.yolo.yolo_dataset_adapter import (
    YoloDatasetAdapter,
)
from ontology.app.ports.input.face_training_use_case import FaceTrainingUseCase
from ontology.app.ports.output.yolo_port import YoloDatasetPort
from ontology.app.use_cases.yolo_interactor import YoloInteractor


def get_face_dataset_port() -> YoloDatasetPort:
    return YoloDatasetAdapter()


def get_face_training_use_case() -> FaceTrainingUseCase:
    return YoloInteractor(dataset_port=get_face_dataset_port())
