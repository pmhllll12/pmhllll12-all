"""이미지 저장소 아웃바운드 포트.

이 인터페이스에는 S3라는 단어가 없다 — 구현을 로컬 디스크나 다른 오브젝트
스토리지로 갈아끼워도 app 계층이 바뀌지 않아야 하기 때문이다.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ImageStorageUnavailableError(RuntimeError):
    """저장소에 접근할 수 없다 — 설정 누락, 자격증명 없음, 저장소 장애 등.

    `botocore` 예외를 라우터까지 올려보내면 인바운드 어댑터가 특정 SDK를 알게 된다.
    그래서 아웃바운드 어댑터가 여기서 정의한 예외로 바꿔서 던진다.
    """


class ImageStoragePort(ABC):
    @abstractmethod
    async def upload(self, content: bytes, filename: str, content_type: str) -> str:
        """이미지를 저장하고 저장소가 부여한 키를 돌려준다."""
        raise NotImplementedError

    @abstractmethod
    async def generate_view_url(self, key: str) -> str:
        """키로 조회할 수 있는 임시 URL을 만든다."""
        raise NotImplementedError
