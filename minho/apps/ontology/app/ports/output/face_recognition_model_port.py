from __future__ import annotations

from abc import ABC, abstractmethod


class FaceRecognitionModelPort(ABC):
    @abstractmethod
    def get_model_path(self) -> str:
        """파인튜닝된 얼굴 인식(분류) YOLO 가중치(.pt) 파일의 절대 경로를 반환한다."""
        raise NotImplementedError
