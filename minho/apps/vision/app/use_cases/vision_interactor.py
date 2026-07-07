from __future__ import annotations

import logging
from datetime import datetime

from vision.app.dtos.vision_dto import (
    AnalyzedImageLog,
    AnalyzeImageCommand,
    AnalyzeImageResult,
)
from vision.app.ports.input.vision_use_case import VisionUseCase
from vision.app.ports.output.image_captioning_port import ImageCaptioningPort
from vision.app.ports.output.image_storage_port import ImageStoragePort
from vision.app.ports.output.vision_port import VisionPort
from vision.domain.analyzed_image import AnalyzedImage

logger = logging.getLogger(__name__)


class VisionInteractor(VisionUseCase):
    def __init__(
        self,
        repository: VisionPort,
        captioner: ImageCaptioningPort,
        storage: ImageStoragePort,
    ) -> None:
        self.repository = repository
        self.captioner = captioner
        self.storage = storage

    async def analyze(self, command: AnalyzeImageCommand) -> AnalyzeImageResult:
        image_key = await self.storage.upload(
            command.content, command.filename, command.mime_type
        )
        caption, tags = await self.captioner.caption(command.content, command.mime_type)

        image = AnalyzedImage(
            filename=command.filename,
            caption=caption,
            tags=tags,
            image_key=image_key,
            analyzed_at=datetime.now(),
        )
        await self.repository.save(
            filename=image.filename,
            caption=image.caption,
            tags=image.tags,
            image_key=image.image_key,
            analyzed_at=image.analyzed_at,
        )
        image_url = await self.storage.get_url(image_key)
        logger.info(
            "[VisionInteractor] analyze filename=%r caption=%r image_key=%r",
            image.filename,
            image.caption,
            image.image_key,
        )
        return AnalyzeImageResult(ok=True, caption=caption, tags=tags, image_url=image_url)

    async def get_logs(self) -> list[AnalyzedImageLog]:
        stored_images = await self.repository.list_recent()
        logs = []
        for item in stored_images:
            image_url = await self.storage.get_url(item.image_key)
            logs.append(
                AnalyzedImageLog(
                    analyzed_at=item.analyzed_at,
                    filename=item.filename,
                    caption=item.caption,
                    tags=item.tags,
                    image_url=image_url,
                )
            )
        return logs
