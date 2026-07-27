from __future__ import annotations

from core.lol.t1_mid_faker_orchestrator import FAKER_MODEL, FakerOrchestrator
from ontology.app.ports.input.judge_use_case import JudgeUseCase
from ontology.app.use_cases.faker_judge_interactor import FakerJudgeInteractor

_SPAM_JUDGE_SYSTEM_PROMPT = (
    "당신은 이메일 스팸 판별 전문가입니다. "
    "주어진 신호를 분석하고 반드시 아래 형식으로만 답하세요.\n"
    "VERDICT: SPAM 또는 HAM\n"
    "REASON: 판단 이유 한 줄"
)


def get_judge_use_case() -> JudgeUseCase:
    """스팸 판정용 Judge — EXAONE 3.5:2.4b 기반."""
    orchestrator = FakerOrchestrator(
        model=FAKER_MODEL,
        system_prompt=_SPAM_JUDGE_SYSTEM_PROMPT,
    )
    return FakerJudgeInteractor(orchestrator=orchestrator)
