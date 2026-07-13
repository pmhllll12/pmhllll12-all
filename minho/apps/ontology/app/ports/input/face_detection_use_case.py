from __future__ import annotations

from abc import ABC, abstractmethod

from vision.app.dtos.face_detection_dto import DetectFacesCommand, DetectFacesResult


class FaceDetectionUseCase(ABC):
    @abstractmethod
    def detect(self, command: DetectFacesCommand) -> DetectFacesResult:
        raise NotImplementedError
