from __future__ import annotations

from ontology.adapter.outbound.resource_adapters.yolo.face_recognition_model_adapter import (
    LocalFaceRecognitionModelAdapter,
)
from ontology.app.ports.input.face_recognition_use_case import FaceRecognitionUseCase
from ontology.app.ports.output.face_recognition_model_port import FaceRecognitionModelPort
from ontology.app.use_cases.face_recognition_interactor import FaceRecognitionInteractor


def get_face_recognition_model_port() -> FaceRecognitionModelPort:
    return LocalFaceRecognitionModelAdapter()


def get_face_recognition_use_case() -> FaceRecognitionUseCase:
    return FaceRecognitionInteractor(model_port=get_face_recognition_model_port())
