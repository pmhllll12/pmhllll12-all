from __future__ import annotations

from abc import ABC, abstractmethod


class ImageStoragePort(ABC):
    @abstractmethod
    async def upload(self, content: bytes, filename: str, mime_type: str) -> str:
        """이미지를 버킷에 저장하고 객체 키를 반환한다."""
        raise NotImplementedError

    @abstractmethod
    async def get_url(self, key: str) -> str:
        """저장된 객체에 임시로 접근할 수 있는 presigned URL을 반환한다."""
        raise NotImplementedError
