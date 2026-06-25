# 하네스 도구화 — 린터/포매터/pre-commit/CI

[`CLAUDE.md`](CLAUDE.md)·[`AGENTS.md`](AGENTS.md)의 4원칙은 글로 적힌 합의일 뿐, 도구가
강제하지 않으면 결국 어겨진다(카파시가 관찰한 "조용한 가정", "과설계", "모호한 완료").
이 문서는 그 원칙들을 실제로 빌드 타임·커밋 타임에 검증하는 설정이 **어디에** 있는지
정리한다.

## 스택별 설정 위치

| 스택 | 린터/포매터 | 아키텍처 검증 | 문서 |
|---|---|---|---|
| `minho` (Python/FastAPI) | `ruff` | `import-linter` (허브/스포크/온톨로지/클린 아키텍처) | [`../minho/_docs/architecture-star-topology.md`](../minho/_docs/architecture-star-topology.md) |
| `www` (Next.js) | `eslint` + `prettier` | — | [`../www/_docs/linting.md`](../www/_docs/linting.md) |
| `pmh_flutter` (Flutter) | `dart analyze` + `dart format` | — | [`../pmh_flutter/_docs/linting.md`](../pmh_flutter/_docs/linting.md) |

## 중요: 서브모듈 경계 때문에 설정이 한 곳에 모이지 않는다

`minho`(`cloud.pmhllll12.api`)와 `www`(`cloud.pmhllll12.www`)는 **별도 git 저장소**(서브모듈)다.
`pmh_flutter`는 서브모듈이 아니라 이 저장소의 일반 디렉터리다 (`git ls-files --stage`로
160000(gitlink) 모드인지 확인하면 구분된다).

- **CI**: GitHub Actions는 각 저장소 자신의 `.github/workflows/`만 본다. 루트
  `.github/`에 `minho/**` 같은 `paths` 필터를 걸어도, 실제 커밋은 `minho`의 별도
  저장소에서 일어나므로 절대 트리거되지 않는다 (슈퍼프로젝트는 서브모듈을 커밋 포인터
  하나로만 본다). 그래서 `minho/.github/workflows/`, `www/.github/workflows/`에 각자
  CI가 있고, `pmh_flutter`(일반 디렉터리)만 루트 `.github/workflows/flutter-lint.yml`에 있다.
- **pre-commit**: 마찬가지로 `pre-commit install`은 그 명령을 실행한 저장소의
  `.git/hooks/`에만 등록된다. `minho/`, `www/`는 각자 `.pre-commit-config.yaml`을 갖고
  그 디렉터리 안에서 `pre-commit install`을 따로 해야 한다. 루트의
  `.pre-commit-config.yaml`은 `pmh_flutter`만 다룬다.

## 로컬에서 전부 켜기

```powershell
# minho
cd minho; pip install -r requirements-dev.txt pre-commit; pre-commit install

# www
cd www; npm install; pip install pre-commit; pre-commit install

# 루트 (pmh_flutter 담당)
cd ..; pip install pre-commit; pre-commit install
```

세 군데 모두 `pre-commit install`을 해야 세 스택이 전부 커밋 시점에 검증된다 — 하나만
하면 나머지 둘은 그냥 통과한다.
