from __future__ import annotations

import asyncio
import io
import logging

from PIL import Image
from ultralytics import YOLO
from vision.app.dtos.face_recognition_dto import PredictFaceCommand, PredictFaceResult
from vision.app.ports.input.face_recognition_use_case import FaceRecognitionUseCase
from vision.app.ports.output.face_recognition_model_port import FaceRecognitionModelPort

logger = logging.getLogger(__name__)


class FaceRecognitionInteractor(FaceRecognitionUseCase):
    def __init__(self, model_port: FaceRecognitionModelPort) -> None:
        self.model_port = model_port
        self._model: YOLO | None = None

    def _get_model(self) -> YOLO:
        if self._model is None:
            self._model = YOLO(self.model_port.get_model_path())
        return self._model

    async def predict(self, command: PredictFaceCommand) -> PredictFaceResult:
        result = await asyncio.to_thread(self._predict_sync, command.content)
        logger.info(
            "[FaceRecognitionInteractor] predict filename=%r predicted_name=%r confidence=%.4f",
            command.filename,
            result.predicted_name,
            result.confidence,
        )
        return result

    def _predict_sync(self, content: bytes) -> PredictFaceResult:
        model = self._get_model()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        results = model.predict(source=image, verbose=False)

        probs = results[0].probs
        top1_index = int(probs.top1)
        predicted_name = results[0].names[top1_index]
        confidence = float(probs.top1conf)

        return PredictFaceResult(ok=True, predicted_name=predicted_name, confidence=confidence)
