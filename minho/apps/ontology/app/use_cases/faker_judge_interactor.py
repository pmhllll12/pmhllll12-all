from __future__ import annotations

import asyncio
import logging
import re

from core.lol.t1_mid_faker_orchestrator import FakerOrchestrator
from ontology.app.ports.input.judge_use_case import JudgeUseCase
from ontology.domain.evidence import Evidence
from ontology.domain.verdict import Verdict

logger = logging.getLogger(__name__)

_VERDICT_RE = re.compile(r"VERDICT\s*:\s*(SPAM|HAM)", re.IGNORECASE)
_REASON_RE = re.compile(r"REASON\s*:\s*(.+)", re.IGNORECASE)


_SPAM_KEYWORDS = re.compile(
    r"(무료|대출|클릭|당첨|이벤트|광고|홍보|할인|쿠폰|링크|http|www\.|\.com|\.net|\.xyz)",
    re.IGNORECASE,
)


def _pre_check(topic: str) -> Verdict | None:
    """LLM 호출 전 단순 규칙으로 명백한 경우를 먼저 처리한다."""
    stripped = topic.strip()
    # 짧은 메시지(30자 미만)에 스팸 키워드 없으면 바로 HAM
    if len(stripped) < 30 and not _SPAM_KEYWORDS.search(stripped):
        return Verdict(label="HAM", confidence=0.05, reason="짧은 일반 메시지로 스팸 가능성 낮음")
    # 스팸 키워드가 명확히 포함되면 바로 SPAM
    if _SPAM_KEYWORDS.search(stripped):
        return None  # LLM에게 넘김
    return None


def _parse_verdict(reply: str) -> Verdict:
    verdict_match = _VERDICT_RE.search(reply)
    # 기본값: 불확실하면 HAM (관리자 대시보드 — 신뢰된 사용자)
    label = verdict_match.group(1).upper() if verdict_match else "HAM"
    reason_match = _REASON_RE.search(reply)
    reason = reason_match.group(1).strip() if reason_match else reply[:120].strip()
    confidence = 0.88 if label == "SPAM" else 0.12
    return Verdict(label=label, confidence=confidence, reason=reason)


class FakerJudgeInteractor(JudgeUseCase):
    """EXAONE 3.5:2.4b(FakerOrchestrator)로 Evidence를 판정하는 인터렉터."""

    def __init__(self, orchestrator: FakerOrchestrator) -> None:
        self._orchestrator = orchestrator

    async def evaluate(self, evidence: Evidence) -> Verdict:
        signals = evidence.signals
        topic = signals.get("topic", "")
        to_email = signals.get("to_email", "")
        context = signals.get("context", "")

        # 사전 규칙으로 빠르게 판단 가능한 경우 LLM 생략
        pre = _pre_check(topic)
        if pre is not None:
            logger.info(
                "[FakerJudgeInteractor] pre-check source=%s label=%s", evidence.source_app, pre.label
            )
            return pre

        prompt = (
            f"당신은 이메일 스팸 판정 전문가입니다.\n"
            f"아래 이메일 발송 요청이 스팸인지 판정하세요.\n\n"
            f"수신자: {to_email}\n"
            f"주제/내용: {topic}\n"
            f"{('참고: ' + context) if context else ''}\n\n"
            f"스팸 기준: 광고·홍보 문구, 악성 URL, 피싱 시도, 불법 성인 콘텐츠.\n"
            f"정상(HAM): 업무 연락, 인사, 일정 안내, 간단한 메시지 등.\n\n"
            f"반드시 아래 형식으로만 답하세요:\n"
            f"VERDICT: SPAM 또는 VERDICT: HAM\n"
            f"REASON: (한 문장 이유)"
        )
        reply = await asyncio.to_thread(self._orchestrator.chat, prompt)
        verdict = _parse_verdict(reply)
        logger.info(
            "[FakerJudgeInteractor] source=%s label=%s confidence=%.2f",
            evidence.source_app,
            verdict.label,
            verdict.confidence,
        )
        return verdict
