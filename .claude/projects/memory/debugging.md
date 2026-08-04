# 디버깅·조사 인사이트

문제 해결·저장소 조사 중 얻은, 다음에 시간 아끼게 해줄 인사이트를 누적한다.

## 일반 템플릿을 정본 문서에 넣기 전엔 실제 저장소와 대조한다

- **맥락**: 일반적인 "Node.js REST API" 형태의 `CLAUDE.md` 템플릿을 받아 루트 정본 `CLAUDE.md`에 추가 요청.
- **함정**: 그대로 붙이면 거짓 정보를 정본에 심게 된다. 실제 조사 결과 이 저장소는 백엔드 `minho`가 **Python/FastAPI**(uvicorn·alembic·`:8000/docs`, 테스트는 **pytest**), 프런트 `www`는 세미콜론 **사용** + 엄격 ESLint, 브랜치는 **main/neo/sigma(develop 없음)**, 환경파일은 **`.env`**(`.env.local` 아님)였다. 템플릿의 Node.js/Jest/develop/세미콜론-없음/`.env.local`은 전부 불일치.
- **적용**: 문서에 추가·수정하기 전 `package.json`·`pyproject.toml`·`docker-compose.yaml`·`git branch -a`·`.env` 키를 먼저 확인해 대조표를 만들고, 근거 없는 항목(예: `src/legacy/`·payments PCI)은 지어내지 말고 생략한다. 저장소 자체의 CLAUDE.md 원칙("침묵 가정 금지")과도 일치.

## 로컬 DB 확인은 호스트 TCP가 아니라 `docker exec psql`로 한다

- **맥락**: 2026-07-30. EC2 개발 머신에서 `moneyball_players` 상태를 확인하려 호스트에서 `localhost:5432`로 붙으려 함.
- **함정**: `pg_hba.conf`는 컨테이너 내부(local/127.0.0.1)만 `trust`이고 그 밖은 `scram-sha-256`이라, 호스트 TCP 연결은 비밀번호를 정확히 줘야 한다. (2026-07-30 이전에는 루트 `.env`의 `POSTGRES_PASSWORD`가 **빈 값**이고 볼륨에 저장된 실제 비밀번호와도 달라 `password authentication failed`로 막혔다 — 아래 항목에서 해소됨.)
- **적용**: `docker exec -i pmhllll12-all-pgvector-1 psql -U postgres -d neondb`로 확인한다. 파괴적 확인이 필요하면 `BEGIN; … ROLLBACK;`으로 감싼다. 파이썬 코드 경로 검증은 DB 없이 `stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})`로 SQL을 뽑아 psql에 넣는 방식이 유용했다.
- 이 머신엔 프로젝트 venv·pytest가 없다 — 스크래치 디렉터리에 `python3.11 -m venv`로 만들어 쓰고 프로젝트는 건드리지 않는다.

## 볼륨의 postgres 비밀번호를 모를 때 데이터를 지키며 복구하는 법

- **맥락**: 2026-07-30. backend 기동 시 `alembic upgrade head` 가 `fe_sendauth: no password supplied` 로 실패. 루트 `.env`의 `POSTGRES_PASSWORD`가 빈 값이라 `docker-compose.yaml:18`의 `DATABASE_URL`이 비번 없이 조립됐다.
- **함정**: 볼륨에 이미 DB가 있으면 postgres 이미지는 `Skipping initialization` 으로 `POSTGRES_PASSWORD` 를 **무시**한다. 그래서 비번이 비어도 컨테이너는 정상 기동해 `docker ps` 로는 멀쩡해 보이고, 앱도 마이그레이션 실패 후 uvicorn 은 계속 띄워 `Application startup complete` 가 찍힌다. **초록불에 속지 말 것.** 볼륨을 지우는 재초기화는 데이터를 날리므로 최후수단이다.
- **적용**: 컨테이너 내부 소켓은 `trust` 이므로 비번을 몰라도 들어갈 수 있다. `printf "ALTER USER postgres PASSWORD '%s';" "$PW" | docker exec -i pmhllll12-all-pgvector-1 psql -U postgres -d neondb` (평문이 argv 에 안 남게 **stdin** 으로 전달, `log_statement=none` 확인). 그 뒤 `.env` 동기화 → `chmod 600 .env` → `docker compose up -d pgvector backend`. 데이터는 named volume `pmhllll12-all_pgvector_data` 에 있어 컨테이너 재생성에도 보존된다.
- **검증**: 변경 **전에** 테이블별 `count(*)` 베이스라인을 떠 두고(통계 뷰 `pg_stat_user_tables`는 비정상 종료 시 0으로 초기화돼 못 믿는다) 사후 대조한다.
