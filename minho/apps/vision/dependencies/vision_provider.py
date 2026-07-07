from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from vision.adapter.outbound.gemini_vision_client import GeminiVisionClient
from vision.adapter.outbound.repositories.vision_repository import VisionRepository
from vision.adapter.outbound.s3_image_storage_client import S3ImageStorageClient
from vision.app.ports.input.vision_use_case import VisionUseCase
from vision.app.ports.output.image_captioning_port import ImageCaptioningPort
from vision.app.ports.output.image_storage_port import ImageStoragePort
from vision.app.ports.output.vision_port import VisionPort
from vision.app.use_cases.vision_interactor import VisionInteractor

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
