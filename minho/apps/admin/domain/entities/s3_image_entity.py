"""업로드된 이미지의 도메인 규칙.

이 계층은 S3도 FastAPI도 모른다 — `boto3`·`UploadFile` 같은 이름이 여기 들어오면
계층 계약(`pyproject.toml`의 `[[tool.importlinter.contracts]]` layers)이 깨진다.
저장 위치가 S3에서 다른 곳으로 바뀌어도 이 파일은 그대로여야 한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

# 허용 이미지 형식. 브라우저가 흔히 보내는 것만 받는다 — SVG는 스크립트를 품을 수
# 있어(저장 후 presigned URL로 그대로 서빙되므로) 의도적으로 제외한다.
ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset(
    {"image/jpeg", "image/png", "image/gif", "image/webp"}
)

# 업로드 상한. 라우터가 요청을 일찍 끊는 데도 쓰고, 유스케이스가 다시 확인한다.
MAX_IMAGE_BYTES = 10 * 1024 * 1024


class ImageUploadRejected(ValueError):
    """도메인 규칙에 어긋나는 업로드. 어댑터가 4xx로 옮긴다."""


def ensure_uploadable(filename: str, content_type: str, size_bytes: int) -> None:
    """저장소에 넣기 **전에** 검사한다.

    업로드가 끝난 뒤 엔티티를 만들면서 검사하면 이미 S3에 올라간 뒤라 늦다.
    """
    if not filename.strip():
        raise ImageUploadRejected("파일 이름이 비어 있습니다.")
    if size_bytes <= 0:
        raise ImageUploadRejected("빈 파일은 업로드할 수 없습니다.")
    if size_bytes > MAX_IMAGE_BYTES:
        raise ImageUploadRejected(
            f"이미지 크기는 {MAX_IMAGE_BYTES // (1024 * 1024)}MB를 초과할 수 없습니다."
        )
    if content_type not in ALLOWED_CONTENT_TYPES:
        allowed = ", ".join(sorted(ALLOWED_CONTENT_TYPES))
        raise ImageUploadRejected(f"지원하지 않는 형식입니다: {content_type!r} (허용: {allowed})")


@dataclass(frozen=True)
class S3ImageEntity:
    """저장이 끝난 이미지 한 건.

    `key`는 저장소가 정한 식별자다 — 도메인은 그 형식을 규정하지 않는다.
    """

    key: str
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ImageUploadRejected("저장소가 키를 반환하지 않았습니다.")
