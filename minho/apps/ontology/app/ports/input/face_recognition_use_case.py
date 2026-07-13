from __future__ import annotations

from abc import ABC, abstractmethod

from vision.app.dtos.face_recognition_dto import PredictFaceCommand, PredictFaceResult


class FaceRecognitionUseCase(ABC):
    @abstractmethod
    async def predict(self, command: PredictFaceCommand) -> PredictFaceResult:
        raise NotImplementedError
