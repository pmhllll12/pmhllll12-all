from __future__ import annotations

import mimetypes
import os
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

# MCP 서버 프로세스와 분류 서비스(FastAPI /api/vision/classify)를 분리 유지하기 위해
# HTTP로 호출한다 — 지금은 같은 프로세스에 마운트돼 있지만 나중에 별도 서비스로
# 떼어내도 이 tool 코드는 바뀔 필요가 없다.
_API_PORT = os.getenv("API_PORT", "8000")
_CLASSIFY_API_BASE_URL = os.getenv("CLASSIFY_API_BASE_URL", f"http://127.0.0.1:{_API_PORT}")
_CLASSIFY_ENDPOINT = f"{_CLASSIFY_API_BASE_URL}/api/vision/classify"

mcp = FastMCP("ImageClassifier")


async def _load_image_bytes(image_path_or_url: str) -> tuple[bytes, str] | str:
    """(content, filename)을 반환하거나, 실패 시 에이전트에게 보여줄 에러 문자열을 반환한다."""
    if image_path_or_url.startswith(("http://", "https://")):
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(
                    image_path_or_url,
                    headers={"User-Agent": "pmhllll12-image-classifier-mcp/1.0"},
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            return f"이미지 URL을 다운로드하지 못했습니다: {image_path_or_url} ({exc})"
        filename = image_path_or_url.rsplit("/", 1)[-1] or "downloaded.jpg"
        return response.content, filename

    path = Path(image_path_or_url)
    if not path.is_file():
        return f"이미지 파일을 찾을 수 없습니다: {image_path_or_url}"
    return path.read_bytes(), path.name


@mcp.tool()
async def classify_image(image_path_or_url: str) -> str:
    """사용자가 이미지의 내용, 카테고리, 종류(예: "이 사진에 뭐가 있어?", "이거 무슨 동물이야?")를
    물어볼 때 사용한다. 입력은 로컬 파일 경로 또는 이미지 URL(http/https)이다.
    ConvNeXt Nano(ImageNet-1k, 1000종)로 분류해 최상위 라벨과 top-5 후보를 반환한다.
    사람 얼굴 인식이나 카카오톡 메시지 같은 다른 종류의 요청에는 사용하지 않는다.
    """
    loaded = await _load_image_bytes(image_path_or_url)
    if isinstance(loaded, str):
        return loaded
    content, filename = loaded
    mime_type = mimetypes.guess_type(filename)[0] or "image/jpeg"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                _CLASSIFY_ENDPOINT,
                files={"file": (filename, content, mime_type)},
            )
    except httpx.ConnectError:
        return "이미지 분류 서비스에 연결할 수 없습니다 (서버가 꺼져 있거나 재시작 중일 수 있음)."
    except httpx.TimeoutException:
        return "이미지 분류 서비스 응답이 시간 초과되었습니다."

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        return f"이미지 분류에 실패했습니다: {detail}"

    data = response.json()
    top5_str = ", ".join(f"{item['label']} ({item['confidence']:.1%})" for item in data["top5"])
    note = " (신뢰도가 낮아 결과가 부정확할 수 있습니다)" if data["uncertain"] else ""
    return f"최상위 예측: {data['label']} ({data['confidence']:.1%}){note}\nTop-5: {top5_str}"
