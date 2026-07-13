from __future__ import annotations

import logging

from ultralytics import YOLO
from ontology.app.dtos.face_training_dto import TrainFaceRecognizerCommand, TrainFaceRecognizerResult
from ontology.app.ports.input.face_training_use_case import FaceTrainingUseCase
from ontology.app.ports.output.yolo_port import YoloDatasetPort

logger = logging.getLogger(__name__)

# YOLOv11 Nano — 파라미터 약 2.6M, 가장 가벼운 백본. 분류(-cls) 데이터셋(인물별 폴더)에 맞춰
# 학습하므로 detect용 yolo11n.pt가 아닌 cls 헤드가 포함된 yolo11n-cls.pt를 사용한다.
_BASE_WEIGHTS = "yolo11n-cls.pt"


class YoloInteractor(FaceTrainingUseCase):
    def __init__(self, dataset_port: YoloDatasetPort) -> None:
        self.dataset_port = dataset_port

    def train(self, command: TrainFaceRecognizerCommand) -> TrainFaceRecognizerResult:
        dataset_root = self.dataset_port.get_dataset_root_path()

        model = YOLO(_BASE_WEIGHTS)
        model.train(
            data=dataset_root,
            epochs=command.epochs,
            batch=command.batch_size,
            imgsz=command.image_size,
        )
        weights_path = str(model.trainer.best)

        logger.info(
            "[YoloInteractor] train epochs=%s weights_path=%s",
            command.epochs,
            weights_path,
        )
        return TrainFaceRecognizerResult(
            ok=True, weights_path=weights_path, epochs=command.epochs
        )
