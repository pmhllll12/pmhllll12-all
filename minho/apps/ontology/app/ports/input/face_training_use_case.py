from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.face_training_dto import TrainFaceRecognizerCommand, TrainFaceRecognizerResult


class FaceTrainingUseCase(ABC):
    @abstractmethod
    def train(self, command: TrainFaceRecognizerCommand) -> TrainFaceRecognizerResult:
        raise NotImplementedError
