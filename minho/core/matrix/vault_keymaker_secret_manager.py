"""전역 API 키·외부 AI 클라이언트를 한 곳에서 관리하는 키메이커."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# google.generativeai 는 /chat 호출 시에만 로드 (서버 기동 시 FutureWarning 방지)
_genai_module: Any = None


def _get_genai() -> Any:
    global _genai_module
    if _genai_module is None:
        import google.generativeai as genai

        _genai_module = genai
    return _genai_module

# backend/apps (matrix/app/keymaker.py → parent×3)
_APPS_ROOT = Path(__file__).resolve().parent.parent.parent

_INVALID_GEMINI_KEYS = frozenset(
    {
        "여기에_복사한_키_붙여넣기",
        "your-api-key-here",
        "changeme",
    }
)

# 무료 티어에서 gemini-2.0-flash 는 limit:0 인 경우가 많음 → 2.5-flash 우선
_DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

# text-embedding-004 는 폐기됨 → gemini-embedding-001 사용.
# 기본 출력은 3072차원이라 output_dimensionality로 pgvector 컬럼 차원(768)에 맞춰 자름.
_EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIM = 768

_FALLBACK_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
)

_LEGACY_GEMINI_MODELS = {
    "gemini-1.5-flash": _DEFAULT_GEMINI_MODEL,
    "gemini-1.5-flash-8b": _DEFAULT_GEMINI_MODEL,
    "gemini-1.5-pro": _DEFAULT_GEMINI_MODEL,
    "gemini-pro": _DEFAULT_GEMINI_MODEL,
    "gemini-2.0-flash": _DEFAULT_GEMINI_MODEL,
}


def _is_retryable_gemini_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return (
        "429" in msg
        or "quota" in msg
        or "resource exhausted" in msg
        or "rate limit" in msg
        or "404" in msg
        or "not found" in msg
    )


def format_gemini_error(exc: Exception) -> tuple[int, str]:
    """(HTTP 상태 코드, 사용자용 메시지)"""
    msg = str(exc)
    lower = msg.lower()
    if "429" in msg or "quota" in lower or "resource exhausted" in lower:
        wait = ""
        m = re.search(r"retry in ([\d.]+)s", msg, re.IGNORECASE)
        if m:
            wait = f" 약 {int(float(m.group(1)))}초 후 다시 시도해 보세요."
        return (
            429,
            "Gemini API 무료 할당량을 초과했습니다. "
            "잠시 후 다시 시도하거나 Google AI Studio에서 사용량·요금제를 확인하세요."
            f"{wait} (https://ai.dev/rate-limit)",
        )
    if "404" in msg or "not found" in lower:
        return (
            502,
            "요청한 Gemini 모델을 사용할 수 없습니다. "
            "backend/apps/.env 의 GEMINI_MODEL 을 gemini-2.5-flash 로 바꿔 보세요.",
        )
    return 502, msg


class Keymaker:
    """시스템 전역에서 사용하는 API 키·Gemini 등 외부 연동을 담당합니다."""

    def __init__(self, apps_root: Path | None = None) -> None:
        self._apps_root = apps_root if apps_root is not None else _APPS_ROOT
        self._env_loaded = False
        self._gemini_model: Any = None
        self._last_model_used: str | None = None

    def load_env(self) -> None:
        if self._env_loaded:
            return
        load_dotenv(self._apps_root / ".env")
        load_dotenv()
        self._env_loaded = True

    @property
    def gemini_api_key(self) -> str | None:
        self.load_env()
        raw = (os.getenv("GEMINI_API_KEY") or "").strip()
        if not raw or raw in _INVALID_GEMINI_KEYS:
            return None
        return raw

    def _normalize_model_name(self, raw: str) -> str:
        name = raw.strip().removeprefix("models/")
        if not name:
            return _DEFAULT_GEMINI_MODEL
        return _LEGACY_GEMINI_MODELS.get(name, name)

    @property
    def gemini_model_name(self) -> str:
        self.load_env()
        raw = (os.getenv("GEMINI_MODEL") or _DEFAULT_GEMINI_MODEL).strip()
        return self._normalize_model_name(raw)

    @property
    def last_model_used(self) -> str:
        return self._last_model_used or self.gemini_model_name

    def _model_candidates(self) -> list[str]:
        preferred = self.gemini_model_name
        seen: set[str] = set()
        ordered: list[str] = []
        for name in (preferred, *_FALLBACK_MODELS):
            if name not in seen:
                seen.add(name)
                ordered.append(name)
        return ordered

    def _ensure_configured(self) -> None:
        key = self.gemini_api_key
        if not key:
            raise MissingApiKeyError(
                "GEMINI_API_KEY 가 없거나 예시 문구 그대로입니다. "
                "backend/apps/.env 에서 GEMINI_API_KEY 를 실제 키로 설정하세요."
            )
        _get_genai().configure(api_key=key)

    def get_gemini_model(self, model_name: str | None = None) -> Any:
        """지정 모델(또는 설정값)의 GenerativeModel 인스턴스."""
        self._ensure_configured()
        name = self._normalize_model_name(model_name or self.gemini_model_name)
        return _get_genai().GenerativeModel(name)

    def _generate_with_retry(self, build_contents: Any) -> tuple[Any, str]:
        """할당량/404 시 다른 Flash 모델로 순서대로 재시도합니다."""
        self._ensure_configured()
        last_exc: Exception | None = None

        for model_name in self._model_candidates():
            try:
                model = _get_genai().GenerativeModel(model_name)
                response = model.generate_content(build_contents())
                self._gemini_model = model
                self._last_model_used = model_name
                return response, model_name
            except Exception as exc:
                if _is_retryable_gemini_error(exc):
                    last_exc = exc
                    continue
                raise

        if last_exc is not None:
            raise last_exc
        raise RuntimeError("Gemini 모델 호출에 실패했습니다.")

    def generate_content(self, prompt: str) -> tuple[Any, str]:
        return self._generate_with_retry(lambda: prompt)

    def generate_vision_content(
        self, prompt: str, image_bytes: bytes, mime_type: str
    ) -> tuple[Any, str]:
        """이미지 + 프롬프트로 멀티모달 응답을 생성합니다."""
        return self._generate_with_retry(
            lambda: [{"mime_type": mime_type, "data": image_bytes}, prompt]
        )

    def embed_content(self, text: str) -> list[float]:
        """텍스트를 `EMBEDDING_DIM` 차원 벡터로 변환합니다 (pgvector 저장용)."""
        self._ensure_configured()
        result = _get_genai().embed_content(
            model=_EMBEDDING_MODEL, content=text, output_dimensionality=EMBEDDING_DIM
        )
        return list(result["embedding"])

    def reset_gemini_cache(self) -> None:
        self._gemini_model = None
        self._last_model_used = None


class MissingApiKeyError(RuntimeError):
    """필수 API 키가 없을 때."""


keymaker = Keymaker()
