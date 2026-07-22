---
type: judge
app: ontology
orchestrator: core/lol/t1_mid_faker_orchestrator.py
links:
  - community
  - soccer
  - silicon_valley
  - star_craft
---

# apps/ontology — Star Topology Judge

`core/lol/t1_mid_faker_orchestrator.py`(EXAONE 3.5:2.4b)와 스포크 앱들을 연결하는
**판정 레이어**다. 스포크는 도메인 지식을 직접 노출하지 않고, 추출한 신호(Evidence)만
이 앱에 전달한다. 온톨로지 Judge는 도메인을 모른 채 신호만 보고 판정(Verdict)을 반환한다.

---

## 역할

```
스포크 (도메인 지식 보유)
  → Evidence(signals) 전달
    → apps/ontology Judge
        → core/lol/FakerOrchestrator (EXAONE 3.5:2.4b)
      → Verdict(label, confidence, reason) 반환
    → 스포크가 자기 도메인에 적용
```

- Judge는 "이메일", "스팸", "결제" 같은 도메인 단어를 모른다.
- `signals: dict[str, str]` 형태의 추상 신호만 받는다.
- 판정 기준은 system_prompt로만 주입된다 — 코드 변경 없이 판정 성격을 바꿀 수 있다.

---

## 헥사고날 레이어

```
apps/ontology/
├── domain/
│   ├── evidence.py     # Evidence 값 객체 — 스포크가 전달하는 추상 신호
│   └── verdict.py      # Verdict 값 객체 — Judge의 판정 결과
├── app/
│   ├── ports/input/
│   │   └── judge_use_case.py      # JudgeUseCase (abstract)
│   └── use_cases/
│       └── faker_judge_interactor.py  # EXAONE로 판정하는 구현체
├── dependencies/
│   └── providers.py    # get_judge_use_case() — FakerOrchestrator 주입
└── tests/
```

**의존성 방향:** `adapter` → `app` → `domain` / `app` → `core/lol`

---

## 스팸 판정 흐름 (community 앱 예시)

```python
evidence = Evidence(
    source_app="community",
    signals={"to_email": "...", "topic": "..."},
)
verdict = await judge.evaluate(evidence)
if verdict.is_spam:
    raise HTTPException(400, detail=verdict.reason)
```

---

## 확장 규칙

새 스포크가 판정을 요청하려면:

1. 스포크 use case에서 `Evidence(signals={...})` 생성
2. `get_judge_use_case()`를 DI로 주입
3. `verdict.label`로 자기 도메인 개념에 매핑

system_prompt만 교체하면 스팸 외 다른 판정(유해 콘텐츠, 결제 이상 등)도 동일 구조로 처리한다.

---

## TDD

`pytest.ini`의 `testpaths`에 포함돼 있어 `cd minho && python -m pytest`만 실행해도 이 앱의
테스트가 함께 돈다. ontology만 골라 돌리려면:

```bash
cd minho
python -m pytest apps/ontology/tests/ -v
```
