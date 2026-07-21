from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.image_classifier_dto import ClassifyImageCommand, ClassifyImageResult


class ImageClassifierUseCase(ABC):
    @abstractmethod
    async def classify(self, command: ClassifyImageCommand) -> ClassifyImageResult:
        raise NotImplementedError
