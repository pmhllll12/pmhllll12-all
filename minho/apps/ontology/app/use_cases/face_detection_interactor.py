from __future__ import annotations

import logging

from ultralytics import YOLO
from ontology.app.dtos.face_detection_dto import (
    DetectFacesCommand,
    DetectFacesResult,
    FaceBoundingBox,
)
from ontology.app.ports.input.face_detection_use_case import FaceDetectionUseCase
from ontology.app.ports.output.face_detection_model_port import FaceDetectionModelPort

logger = logging.getLogger(__name__)


class FaceDetectionInteractor(FaceDetectionUseCase):
    def __init__(self, model_port: FaceDetectionModelPort) -> None:
        self.model_port = model_port
        self._model: YOLO | None = None

    def _get_model(self) -> YOLO:
        if self._model is None:
            self._model = YOLO(self.model_port.get_model_path())
        return self._model

    def detect(self, command: DetectFacesCommand) -> DetectFacesResult:
        model = self._get_model()
        results = model.predict(
            source=command.image_path, conf=command.confidence, verbose=False
        )

        boxes: list[FaceBoundingBox] = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                boxes.append(
                    FaceBoundingBox(
                        x1=x1, y1=y1, x2=x2, y2=y2, confidence=float(box.conf[0])
                    )
                )

        logger.info(
            "[FaceDetectionInteractor] detect image_path=%r found=%d",
            command.image_path,
            len(boxes),
        )
        return DetectFacesResult(ok=True, boxes=boxes)
