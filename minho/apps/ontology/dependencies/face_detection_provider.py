from __future__ import annotations

from ontology.adapter.outbound.resource_adapters.yolo.face_detection_model_adapter import (
    LocalFaceDetectionModelAdapter,
)
from ontology.app.ports.input.face_detection_use_case import FaceDetectionUseCase
from ontology.app.ports.output.face_detection_model_port import FaceDetectionModelPort
from ontology.app.use_cases.face_detection_interactor import FaceDetectionInteractor


def get_face_detection_model_port() -> FaceDetectionModelPort:
    return LocalFaceDetectionModelAdapter()


def get_face_detection_use_case() -> FaceDetectionUseCase:
    return FaceDetectionInteractor(model_port=get_face_detection_model_port())
