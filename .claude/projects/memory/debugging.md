# 디버깅·조사 인사이트

문제 해결·저장소 조사 중 얻은, 다음에 시간 아끼게 해줄 인사이트를 누적한다.

## 일반 템플릿을 정본 문서에 넣기 전엔 실제 저장소와 대조한다

- **맥락**: 일반적인 "Node.js REST API" 형태의 `CLAUDE.md` 템플릿을 받아 루트 정본 `CLAUDE.md`에 추가 요청.
- **함정**: 그대로 붙이면 거짓 정보를 정본에 심게 된다. 실제 조사 결과 이 저장소는 백엔드 `minho`가 **Python/FastAPI**(uvicorn·alembic·`:8000/docs`, 테스트는 **pytest**), 프런트 `www`는 세미콜론 **사용** + 엄격 ESLint, 브랜치는 **main/neo/sigma(develop 없음)**, 환경파일은 **`.env`**(`.env.local` 아님)였다. 템플릿의 Node.js/Jest/develop/세미콜론-없음/`.env.local`은 전부 불일치.
- **적용**: 문서에 추가·수정하기 전 `package.json`·`pyproject.toml`·`docker-compose.yaml`·`git branch -a`·`.env` 키를 먼저 확인해 대조표를 만들고, 근거 없는 항목(예: `src/legacy/`·payments PCI)은 지어내지 말고 생략한다. 저장소 자체의 CLAUDE.md 원칙("침묵 가정 금지")과도 일치.
