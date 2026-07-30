# 로컬 PostgreSQL(pgvector) → EC2 Docker pgvector 마이그레이션

로컬 PostgreSQL의 테이블을 EC2의 `pgvector` 컨테이너로 옮기는 절차. 가장 안전하고 단순한
방식은 **`pg_dump` → 파일 전송 → `pg_restore`** 다. `vector` 타입 컬럼도 양쪽에 확장이
설치돼 있으면 `pg_dump` 가 그대로 처리한다.

---

## 0. 시작 전 — 방향과 덮어쓸 데이터 확인

> **경고.** 이 절차는 **EC2 쪽 데이터를 로컬 값으로 대체**한다. 2026-07-30 기준 EC2의
> `moneyball_players` 는 **480행 / `embedding` 480행 모두 채워진 상태**다(Gemini
> `gemini-embedding-001`, 768차원). 로컬 테이블의 `embedding` 이 NULL이면 복원 후 EC2도
> 전부 NULL로 되돌아간다. 옮기려는 방향이 맞는지 먼저 확인하고, **4단계 전에 반드시 EC2
> 쪽 백업을 뜬다.**

EC2 현재 상태를 확인하는 명령:

```bash
docker exec pmhllll12-all-pgvector-1 psql -U postgres -d neondb \
  -c "select * from moneyball_player_embedding_summary;"
```

### EC2 쪽 확인된 값 (`docker-compose.yaml` 기준)

| 항목 | 값 |
|------|-----|
| 컨테이너 | `pmhllll12-all-pgvector-1` (이미지 `pgvector/pgvector:pg17`) |
| DB 유저 / DB명 | `postgres` / `neondb` |
| 서버 버전 | PostgreSQL 17.10 (`pg_dump`·`pg_restore` 도 17.10) |
| `vector` 확장 | 0.8.5 |
| 호스트 포트 | `5432` (compose `ports`) |

로컬에서도 같은 값을 확인해 둔다 — **버전이 어긋나면 4단계에서 깨진다**:

```bash
psql -h localhost -U <로컬유저명> -d <로컬DB명> -c "select version();"
psql -h localhost -U <로컬유저명> -d <로컬DB명> -c "select extversion from pg_extension where extname='vector';"
pg_dump --version
```

- 로컬 서버가 **EC2보다 상위 메이저**(예: PG 18)면 그 덤프는 17.10 `pg_restore` 로 복원할 수
  없다. 이 경우 `-F p`(평문 SQL)로 뽑아 `psql` 로 넣거나, 로컬에 17 계열 `pg_dump` 를 쓴다.
- 로컬 `vector` 확장이 0.8.5보다 높아도 `vector` **타입 자체**는 호환되지만, 새 버전에서
  추가된 연산자·인덱스 옵션을 쓰고 있으면 그 DDL은 복원되지 않는다.

---

## 1단계: 로컬에서 덤프 뜨기

로컬 PowerShell 또는 WSL에서:

```bash
pg_dump -h localhost -U <로컬유저명> -d <로컬DB명> \
  -t moneyball_players -F c -f moneyball_players.dump
```

- `-F c` — custom format(압축·선택 복원 가능)
- `-t moneyball_players` — 이 테이블만. 전체 DB를 옮기려면 `-t` 를 뺀다
- `-t` 로 테이블만 뽑으면 **`CREATE EXTENSION vector` 는 덤프에 들어가지 않는다** → 3단계 필수

비밀번호는 명령줄에 쓰지 않는다. `PGPASSWORD` 환경변수나 `~/.pgpass`(Windows는
`%APPDATA%\postgresql\pgpass.conf`, 권한 600)를 쓴다.

## 2단계: EC2로 파일 전송

```bash
scp -o ProxyCommand="cloudflared access ssh --hostname ssh.pmhllll12.cloud" \
  moneyball_players.dump ec2-user@ip-10-0-0-251:~/
```

`~/.ssh/config` 에 `pmh-server` alias를 두었다면:

```bash
scp moneyball_players.dump pmh-server:~/
```

## 3단계: 컨테이너에 `vector` 확장 확인

```bash
docker exec -it pmhllll12-all-pgvector-1 psql -U postgres -d neondb \
  -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

> **호스트에서 `psql -h localhost -U postgres` 로 붙지 말 것.** 현재 이 서버는 볼륨에
> 저장된 비밀번호가 루트 `.env`·컨테이너 env 값과 어긋나 있어 TCP 접속은
> `password authentication failed` 로 막힌다. `pg_hba.conf` 는 컨테이너 내부의
> `local` / `127.0.0.1` 만 `trust` 이므로 **`docker exec` 로 실행하면 비밀번호가 필요 없다.**
> (비밀번호 정합성은 별도 과제다. 맞추기 전까지는 모든 DB 작업을 `docker exec` 로 한다.)

## 4단계: 복원

### 4-1. 먼저 EC2 쪽 백업 (되돌릴 수 있게)

```bash
STAMP=$(date +%Y%m%d_%H%M)
docker exec pmhllll12-all-pgvector-1 pg_dump -U postgres -d neondb \
  -t moneyball_players -F c -f /tmp/ec2_backup_$STAMP.dump
docker cp pmhllll12-all-pgvector-1:/tmp/ec2_backup_$STAMP.dump ~/
```

### 4-2. 덤프 파일을 컨테이너로 복사

```bash
docker cp ~/moneyball_players.dump pmhllll12-all-pgvector-1:/tmp/
```

### 4-3. 복원 — 데이터만 넣는 방식 (권장)

`moneyball_players` 에는 **의존하는 뷰가 있어** 테이블을 DROP하는 경로는 그냥 실패한다
(아래 "함정" 참고). 테이블을 비우고 데이터만 넣으면 뷰·인덱스·권한이 그대로 유지된다.

```bash
docker exec -it pmhllll12-all-pgvector-1 psql -U postgres -d neondb \
  -c "TRUNCATE moneyball_players;"
docker exec -it pmhllll12-all-pgvector-1 pg_restore -U postgres -d neondb \
  --data-only -t moneyball_players -v /tmp/moneyball_players.dump
```

- `TRUNCATE` 를 건너뛰면 기존 행과 PK가 충돌해 복원이 깨진다
- `moneyball_players` 를 참조하는 FK는 없다(`players → teams → stadiums` 방향) — 그래서
  `TRUNCATE` 에 `CASCADE` 가 필요 없다

### 4-4. 복원 — 테이블째 갈아끼우는 방식 (`--clean`)

스키마까지 로컬 것으로 바꿔야 할 때만. **뷰를 먼저 지우고, 복원 후 다시 만든다.**

```bash
# 1) 의존 뷰 제거
docker exec -it pmhllll12-all-pgvector-1 psql -U postgres -d neondb -c \
  "DROP VIEW IF EXISTS moneyball_player_embedding_summary, moneyball_player_embedding_status;"

# 2) 복원
docker exec -it pmhllll12-all-pgvector-1 pg_restore -U postgres -d neondb \
  --clean --if-exists -v /tmp/moneyball_players.dump

# 3) 뷰 재생성 — 마이그레이션이 CREATE OR REPLACE VIEW 라 그대로 다시 적용하면 된다
cd minho && alembic upgrade head
```

`alembic upgrade head` 를 쓸 수 없는 상황이면
[`../alembic/versions/20260730_0001_create_player_embedding_status_views.py`](../alembic/versions/20260730_0001_create_player_embedding_status_views.py)
의 `_STATUS_VIEW` · `_SUMMARY_VIEW` SQL을 그대로 실행한다.

## 5단계: 검증

```bash
docker exec pmhllll12-all-pgvector-1 psql -U postgres -d neondb \
  -c "select count(*) from moneyball_players;" \
  -c "select * from moneyball_player_embedding_summary;" \
  -c "select player_id, player_name, vector_dims(embedding) from moneyball_players
      where embedding is not null limit 3;"
```

확인 항목:

- 행 수 **480**
- `moneyball_player_embedding_summary.status_message` 가 `✅ 임베딩 완료 — 전체 선수 채워짐`
- `vector_dims(embedding)` 가 **768** (컬럼 정의·`keymaker.EMBEDDING_DIM` 과 일치)

임베딩이 의미 있게 들어왔는지는 유사도 검색으로 한 번 더 확인할 수 있다 — 같은 팀·같은
포지션 선수가 상위에 올라와야 정상이다:

```sql
WITH q AS (SELECT embedding FROM moneyball_players WHERE player_id = '2000001')
SELECT p.player_name, p.position, t.team_name,
       round((p.embedding <=> (SELECT embedding FROM q))::numeric, 4) AS cosine_distance
FROM moneyball_players p LEFT JOIN moneyball_teams t ON p.team_id = t.team_id
WHERE p.player_id <> '2000001'
ORDER BY p.embedding <=> (SELECT embedding FROM q) LIMIT 5;
```

값이 다 NULL이면 로컬 덤프에 임베딩이 없었던 것이다. 그때는
[`../scripts/backfill_player_embeddings.py`](../scripts/backfill_player_embeddings.py) 로 다시 채운다:

```bash
cd minho
python scripts/backfill_player_embeddings.py --dry-run   # 대상 확인
python scripts/backfill_player_embeddings.py --sleep 1   # 실제 채우기
```

---

## 함정 (실제로 확인한 것)

**1. `pg_restore --clean` 은 뷰 의존성 때문에 그냥 실패한다.**

```
ERROR:  cannot drop table moneyball_players because other objects depend on it
DETAIL:  view moneyball_player_embedding_status depends on table moneyball_players
         view moneyball_player_embedding_summary depends on table moneyball_players
HINT:  Use DROP ... CASCADE to drop the dependent objects too.
```

→ 4-3(데이터만 복원)을 쓰거나, 4-4처럼 뷰를 먼저 지우고 복원 후 재생성한다. `DROP ... CASCADE`
로 밀어버리면 뷰가 조용히 사라져 pgAdmin에서 상태 확인이 안 되므로 권하지 않는다.

**2. 호스트에서 `localhost:5432` 로 붙으면 비밀번호 인증에 실패한다.** 3단계 경고 참고 —
`docker exec` 로 우회한다.

**3. `-t 테이블` 덤프에는 확장이 포함되지 않는다.** 3단계(`CREATE EXTENSION`)를 건너뛰면
`type "vector" does not exist` 로 깨진다.

**4. `--data-only` 복원 전에 `TRUNCATE` 를 안 하면** PK 중복으로 실패한다.

**5. `UPDATE` 된 행은 힙 끝으로 밀린다.** 복원·백필 후 pgAdmin의 "First 100 Rows"(정렬 없는
조회)로 보면 앞쪽이 전부 NULL처럼 보일 수 있다. 항상 `moneyball_player_embedding_status`
뷰나 `ORDER BY` 를 명시한 쿼리로 확인한다.

## 비밀번호 취급

- 명령줄에 평문으로 남기지 않는다 — `PGPASSWORD` 또는 `~/.pgpass`(권한 600)를 쓴다
- pgAdmin의 `pgpass` 파일은 이미 `.gitignore` 에 있다. 커밋에 섞이지 않게 유지한다
- 루트 `.env` 의 `POSTGRES_PASSWORD` 는 2026-07-30 에 정리됐다 — 볼륨의 실제 비밀번호를
  `ALTER USER` 로 재설정하고 `.env`(권한 600)와 맞췄다. 두 값은 이제 일치한다
- 다시 어긋나면(빈 값·`fe_sendauth: no password supplied`) 볼륨을 지우지 말고
  `docker exec` 의 `trust` 경로로 들어가 `ALTER USER postgres PASSWORD …` 후 `.env` 를
  동기화하고 `docker compose up -d pgvector backend` 로 재생성한다. 데이터는 보존된다
