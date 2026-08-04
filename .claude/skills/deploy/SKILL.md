---
name: deploy
description: |
  pmhllll12-all 프로덕션 배포를 수행한다.
  배포 전 테스트·린트·빌드를 실행하고, 백엔드는 GitHub Actions(minho-deploy)로,
  전체 스택은 docker compose로 배포한 뒤 헬스체크로 완료를 검증한다.
argument-hint: "[backend|frontend|all]"
disable-model-invocation: true   # 배포는 위험 작업 — Claude 자동 실행 금지, 수동 호출만
user-invocable: true             # 슬래시 메뉴에서 사용자가 직접 호출
allowed-tools:
  - Bash
  - Read
model: sonnet
---

# deploy — pmhllll12-all 배포

프로덕션 배포는 되돌리기 어렵다. **각 단계의 검증이 통과할 때만 다음으로 넘어간다.**
인자(`$1`)로 대상을 받는다: `backend`(기본) · `frontend` · `all`.

---

## 배포 경로 (실제 인프라)

- **백엔드(`minho`)** — GitHub Actions `.github/workflows/minho-deploy.yml`.
  `main`에 `minho/**` 변경이 머지되면 자동 실행되고, `workflow_dispatch`로 수동 실행도 가능.
  Docker Hub(`pmhllll12/minho-backend`) 빌드/푸시 → self-hosted 러너에서 컨테이너 재기동.
- **전체 스택 / 프런트(`www`)** — 운영 서버에서 `docker compose up --build -d`.
  별도 프런트 전용 워크플로는 없다.

---

## 절차

### 1. 사전 점검
- 현재 브랜치와 워킹 트리 상태 확인: `git status --short && git branch --show-current`.
- 커밋되지 않은 변경이 있으면 사용자에게 알리고 멈춘다(배포는 커밋된 상태 기준).

### 2. 테스트·린트·빌드 (대상에 해당하는 것만)
- 백엔드: `cd minho && python -m pytest`  (testpaths: `apps/titanic/tests`)
- 프런트: `npm run lint --prefix www && npm run build --prefix www`
- 하나라도 실패하면 **배포를 중단**하고 실패 출력을 그대로 보고한다.

### 3. 배포 실행
- **backend**:
  - 정석은 `main` 머지지만, 수동 배포는
    `gh workflow run minho-deploy.yml --ref main`.
  - 진행 상황: `gh run list --workflow=minho-deploy.yml -L 1` → `gh run watch <run-id>`.
- **frontend / all**:
  - 운영 서버에서 `docker compose up --build -d frontend gateway`(프런트) 또는
    `docker compose up --build -d`(전체).
  - 이 명령은 self-hosted 서버에서 실행해야 한다. 로컬이면 사용자에게 서버 실행을 요청한다.

### 4. 헬스체크 (완료 조건)
- 백엔드: `curl -sf https://api.pmhllll12.cloud/ping`  (로컬 검증 시 `http://localhost:8000/ping`).
  워크플로도 `/ping`을 최대 15회(2초 간격) 재시도한다.
- 프런트/게이트웨이: `curl -sf http://localhost:3000` (또는 공개 도메인).
- 200이 확인돼야 "배포 완료"라고 말한다. 실패면 실패로 보고한다.

### 5. 실패 시
- GitHub Actions 실패: `gh run view <run-id> --log-failed`로 원인 확인.
- 컨테이너 문제: 이전 이미지 태그(`pmhllll12/minho-backend:<이전 sha>`)로 재기동해 롤백할 수 있음을 안내한다.

---

## 주의
- `.env`/시크릿 값을 출력하거나 커밋하지 않는다. 운영 시크릿은 GitHub Actions Secrets에만 둔다.
- 배포 대상이 모호하면(대상 인자 없음·브랜치가 `main`이 아님 등) 진행 전에 사용자에게 확인한다.
