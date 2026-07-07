import os
from pathlib import Path

import ollama
from dotenv import load_dotenv
from kiwipiepy import Kiwi

# minho/.env / minho/apps/.env — OLLAMA_MODEL 등
_root = Path(__file__).resolve().parent
load_dotenv(_root / ".env")
load_dotenv(_root / "apps" / ".env")

# 1. 한국어 형태소 분석기 Kiwi 초기화
kiwi = Kiwi()

# 레지스트리 기본 후보 (로컬에 없으면 _pick_model 이 설치된 모델로 대체)
DEFAULT_OLLAMA_MODEL = "qwen2.5:3b"

_OLLAMA_MODEL_PLACEHOLDERS = frozenset(
    {
        "설치한_모델_이름",
        "설치된_모델이름",
        "설치된_모델_이름",
    }
)


def _resolve_ollama_model() -> str:
    raw = (os.getenv("OLLAMA_MODEL") or "").strip()
    if not raw:
        return DEFAULT_OLLAMA_MODEL
    if raw in _OLLAMA_MODEL_PLACEHOLDERS:
        print(
            f"[경고] OLLAMA_MODEL 이 예시 문구({raw!r})로 설정되어 있습니다. "
            f"기본 후보를 사용합니다: {DEFAULT_OLLAMA_MODEL}"
        )
        return DEFAULT_OLLAMA_MODEL
    if any("\uac00" <= ch <= "\ud7a3" for ch in raw):
        print(
            f"[경고] OLLAMA_MODEL 에 한글이 포함되어 있습니다({raw!r}). "
            f"기본 후보를 사용합니다: {DEFAULT_OLLAMA_MODEL}"
        )
        return DEFAULT_OLLAMA_MODEL
    return raw


def _installed_model_names() -> list[str]:
    """로컬 Ollama 에 pull 된 모델 이름 목록."""
    try:
        r = ollama.list()
    except Exception as exc:
        raise SystemExit(
            "Ollama 서버에 연결할 수 없습니다. Ollama 앱이 실행 중인지 확인하세요.\n"
            f"상세: {exc}"
        ) from exc
    out: list[str] = []
    for m in getattr(r, "models", None) or []:
        name = getattr(m, "model", None)
        if isinstance(name, str) and name.strip():
            out.append(name.strip())
    return out


def _pick_model(requested: str) -> str:
    """요청 이름이 없으면 한국어/EEVE 계열 → 아무거나 순으로 자동 선택."""
    names = _installed_model_names()
    if not names:
        raise SystemExit(
            "로컬에 설치된 Ollama 모델이 없습니다. 예:\n"
            "  ollama pull anpigon/eeve-korean-10.8b\n"
            "  ollama pull llama3.2\n"
            "설치 후 `ollama list` 로 이름을 확인하세요."
        )
    if requested in names:
        return requested
    for hint in ("eeve", "korean", "yanolja"):
        for n in names:
            if hint in n.lower():
                print(f"[안내] {requested!r} 은(는) 로컬에 없음 → 사용: {n!r}")
                return n
    pick = names[0]
    print(f"[안내] {requested!r} 은(는) 로컬에 없음 → 사용: {pick!r}")
    return pick


def run_korean_ai(user_text: str) -> str:
    print("\n--- [1단계] 입력 문장 전처리 중... ---")

    cleaned_text = kiwi.space(user_text)
    print(f"원본 문장: {user_text}")
    print(f"정제된 문장: {cleaned_text}")

    tokens = kiwi.tokenize(cleaned_text)
    nouns = [t.form for t in tokens if t.tag.startswith("NN")]
    print(f"추출된 핵심 명사: {nouns}")

    requested = _resolve_ollama_model()
    model = _pick_model(requested)
    print(f"\n--- [2단계] Ollama 추론 중... (model={model}) ---")

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": cleaned_text,
                }
            ],
        )
    except ollama.ResponseError as e:
        code = getattr(e, "status_code", None)
        if code == 404:
            names = _installed_model_names()
            raise SystemExit(
                f"모델을 찾을 수 없습니다: {model!r}\n"
                f"현재 로컬 모델: {names or '(없음)'}\n"
                "  ollama pull 로 설치하거나, minho/.env 에 OLLAMA_MODEL=ollama_list에_나온_이름"
            ) from e
        if code == 400 and "model" in str(e).lower():
            raise SystemExit(
                f"잘못된 모델 이름입니다: {model!r}\n"
                "  Remove-Item Env:OLLAMA_MODEL\n"
                "  또는 minho/.env 의 OLLAMA_MODEL 을 ollama list 이름과 동일하게 수정"
            ) from e
        raise

    if hasattr(response, "message") and response.message is not None:
        return (response.message.content or "").strip()
    if isinstance(response, dict):
        return str(response.get("message", {}).get("content", "")).strip()
    return ""


if __name__ == "__main__":
    question = "자연어처리는 넘흐 재밌어요. 올라마와 키위 라이브러리의 장점을 짧게 요약해줘."
    answer = run_korean_ai(question)

    print("\n--- [3단계] AI 최종 답변 ---")
    print(answer)
