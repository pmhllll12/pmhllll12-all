from __future__ import annotations

from abc import ABC, abstractmethod


class ImageClassifierModelPort(ABC):
    @abstractmethod
    def get_model_path(self) -> str:
        """ONNX로 변환된 ConvNeXt Nano 이미지 분류 모델(.onnx) 파일의 절대 경로를 반환한다."""
        raise NotImplementedError
