from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ontology.adapter.outbound.gemini_vision_client import GeminiVisionClient
from ontology.adapter.outbound.repositories.vision_repository import VisionRepository
from ontology.adapter.outbound.s3_image_storage_client import S3ImageStorageClient
from ontology.app.ports.input.vision_use_case import VisionUseCase
from ontology.app.ports.output.image_captioning_port import ImageCaptioningPort
from ontology.app.ports.output.image_storage_port import ImageStoragePort
from ontology.app.ports.output.vision_port import VisionPort
from ontology.app.use_cases.vision_interactor import VisionInteractor

from database import get_db


def get_vision_repository(db: AsyncSession = Depends(get_db)) -> VisionPort:
    return VisionRepository(session=db)


def get_image_captioning_port() -> ImageCaptioningPort:
    return GeminiVisionClient()


def get_image_storage_port() -> ImageStoragePort:
    return S3ImageStorageClient()


def get_vision_use_case(
    repository: VisionPort = Depends(get_vision_repository),
    captioner: ImageCaptioningPort = Depends(get_image_captioning_port),
    storage: ImageStoragePort = Depends(get_image_storage_port),
) -> VisionUseCase:
    return VisionInteractor(repository=repository, captioner=captioner, storage=storage)
