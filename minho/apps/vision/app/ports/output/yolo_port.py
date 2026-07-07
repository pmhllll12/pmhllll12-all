from __future__ import annotations

from abc import ABC, abstractmethod


class YoloDatasetPort(ABC):
    @abstractmethod
    def get_dataset_root_path(self) -> str:
        """`train/<인물명>/*.jpg`, `val/<인물명>/*.jpg` 구조를 가진 데이터셋 루트 디렉터리의
        절대 경로를 반환한다."""
        raise NotImplementedError
