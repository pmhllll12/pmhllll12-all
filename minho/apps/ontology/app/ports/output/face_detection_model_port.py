from __future__ import annotations

from abc import ABC, abstractmethod


class FaceDetectionModelPort(ABC):
    @abstractmethod
    def get_model_path(self) -> str:
        """사전학습된 얼굴 탐지 YOLO 가중치(.pt) 파일의 절대 경로를 반환한다."""
        raise NotImplementedError
