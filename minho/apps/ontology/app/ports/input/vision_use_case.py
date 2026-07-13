from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.vision_dto import (
    AnalyzedImageLog,
    AnalyzeImageCommand,
    AnalyzeImageResult,
)


class VisionUseCase(ABC):
    @abstractmethod
    async def analyze(self, command: AnalyzeImageCommand) -> AnalyzeImageResult:
        raise NotImplementedError

    @abstractmethod
    async def get_logs(self) -> list[AnalyzedImageLog]:
        raise NotImplementedError
