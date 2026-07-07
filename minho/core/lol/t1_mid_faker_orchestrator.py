"""
T1 미드라이너 페이커 오케스트레이터 — EXAONE 3.5:2.4b 로컬 모델 기반.

사용법:
    python -m core.lol.t1_mid_faker_orchestrator
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Generator

import ollama

logger = logging.getLogger(__name__)

FAKER_MODEL = "exaone3.5:2.4b"

_SYSTEM_PROMPT = (
    "당신은 T1의 미드라이너 페이커입니다. "
    "롤(League of Legends) 전략, 챔피언 선택, 라인전 운영에 대해 전문적으로 답합니다. "
    "간결하고 핵심적인 조언을 제공하세요."
)


@dataclass
class FakerOrchestrator:
    """EXAONE 3.5:2.4b를 오케스트레이터로 등록한 T1 미드 전략 에이전트."""

    model: str = FAKER_MODEL
    system_prompt: str = _SYSTEM_PROMPT
    history: list[dict[str, str]] = field(default_factory=list)

    def _build_messages(self, user_text: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.system_prompt},
            *self.history,
            {"role": "user", "content": user_text},
        ]

    def chat(self, user_text: str) -> str:
        """단일 턴 응답 (히스토리 유지)."""
        messages = self._build_messages(user_text)
        try:
            response = ollama.chat(model=self.model, messages=messages)
        except ollama.ResponseError as exc:
            status = getattr(exc, "status_code", None)
            if status == 404:
                raise RuntimeError(
                    f"모델을 찾을 수 없습니다: {self.model!r}\n"
                    "  ollama pull exaone3.5:2.4b  로 먼저 설치하세요."
                ) from exc
            raise

        reply: str = ""
        if hasattr(response, "message") and response.message is not None:
            reply = (response.message.content or "").strip()
        elif isinstance(response, dict):
            reply = str(response.get("message", {}).get("content", "")).strip()

        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": reply})
        logger.debug("[FakerOrchestrator] model=%s turn=%d", self.model, len(self.history) // 2)
        return reply

    def stream(self, user_text: str) -> Generator[str, None, None]:
        """스트리밍 응답 — 토큰 단위로 yield."""
        messages = self._build_messages(user_text)
        full_reply: list[str] = []
        for chunk in ollama.chat(model=self.model, messages=messages, stream=True):
            token: str = ""
            if hasattr(chunk, "message") and chunk.message is not None:
                token = chunk.message.content or ""
            elif isinstance(chunk, dict):
                token = chunk.get("message", {}).get("content", "") or ""
            if token:
                full_reply.append(token)
                yield token

        reply = "".join(full_reply).strip()
        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": reply})

    def reset(self) -> None:
        """대화 히스토리 초기화."""
        self.history.clear()


def _verify_model(model: str) -> bool:
    """Ollama에 해당 모델이 설치되어 있는지 확인."""
    try:
        installed = [
            getattr(m, "model", "")
            for m in (getattr(ollama.list(), "models", None) or [])
        ]
        return model in installed
    except Exception:
        return False


def get_faker_orchestrator() -> FakerOrchestrator:
    """의존성 주입용 팩토리 — EXAONE 3.5:2.4b가 설치되어 있을 때만 반환."""
    if not _verify_model(FAKER_MODEL):
        raise RuntimeError(
            f"EXAONE 모델({FAKER_MODEL})이 로컬에 없습니다.\n"
            "  ollama pull exaone3.5:2.4b"
        )
    return FakerOrchestrator()


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.INFO)
    orchestrator = get_faker_orchestrator()
    print(f"[FakerOrchestrator] 모델: {orchestrator.model} 준비 완료\n")

    questions = [
        "아지르로 미드 라인전 어떻게 해?",
        "로밍 타이밍은 언제가 좋아?",
    ]
    for q in questions:
        print(f"Q: {q}")
        print(f"A: {orchestrator.chat(q)}\n")
