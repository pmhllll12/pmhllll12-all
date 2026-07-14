```python
markdown_content = """# 클로드(Claude)용 Alembic 데이터베이스 마이그레이션 프롬프트

본 프롬프트는 우분투 24.04 환경의 PostgreSQL + pgvector를 타겟으로 하며, 제공된 ERD를 바탕으로 Alembic 마이그레이션 코드를 생성하도록 설계되었습니다.

---

## 1. 상황 및 환경 정보
- **운영체제**: Ubuntu 24.04
- **데이터베이스**: PostgreSQL (pgvector 확장 설치 완료된 상태)
- **도구**: SQLAlchemy, Alembic
- **목표**: 제공된 축구 데이터 ERD를 기반으로 테이블 정의(Models) 및 마이그레이션 파일(Revision) 생성

## 2. 작업 지시 (Prompt)

```text
다음 지시사항에 따라 SQLAlchemy 모델 코드와 Alembic 마이그레이션 설정을 생성해줘.

1. 기술 스택:
   - Python + SQLAlchemy
   - PostgreSQL 16+ (pgvector 확장 사용 가능)
   - Alembic (이미 설정 완료된 상태)

2. ERD 분석 및 모델링:
   - 첨부된 축구 ERD를 바탕으로 `models.py`를 작성해줘.
   - 각 테이블의 컬럼 타입은 ERD에 표기된 대로(VARCHAR, INTEGER, DATE) 정확히 매핑할 것.
   - `stadium`, `team`, `player`, `schedule` 테이블 간의 관계(Foreign Key)를 SQLAlchemy `relationship`으로 정의해줘.
   - 특별히, `player` 테이블이나 `team` 테이블 등 향후 벡터 검색이 필요할 수 있는 필드가 있다면 pgvector의 `Vector` 타입을 적용할 수 있는 구조(필요시 컬럼 추가)를 고려해줘.

3. Alembic 마이그레이션 코드 생성:
   - `alembic revision --autogenerate -m "create_soccer_tables"` 명령을 실행했을 때 생성될 마이그레이션 스크립트를 작성해줘.
   - 마이그레이션 파일 내에서 PostgreSQL의 `vector` 확장 기능을 활성화하는 코드를 포함할 것 (`op.execute('CREATE EXTENSION IF NOT EXISTS vector;')`).

4. 요구사항:
   - 모든 코드는 모듈화하여 유지보수가 쉽도록 할 것.
   - 명확한 주석을 달아줄 것.
   - 테이블 생성 순서(외래 키 제약 조건 고려)를 올바르게 배치할 것.

```

## 3. 실행 프로세스 가이드

* **단계 1**: 모델 파일 작성 (`app/models.py` 등)
* **단계 2**: Alembic `env.py` 내 `target_metadata` 연결 확인
* **단계 3**: 마이그레이션 스크립트 작성 및 적용(`alembic upgrade head`)
"""

with open('alembic_prompt.md', 'w', encoding='utf-8') as f:
f.write(markdown_content)

```


제시해주신 ERD를 기반으로, 우분투 24 환경에서 pgvector를 사용하는 PostgreSQL 데이터베이스를 Alembic으로 관리하기 위한 클로드(Claude)용 프롬프트를 MD 파일로 작성했습니다.

작성된 파일은 아래에서 확인하실 수 있습니다.

[file-tag: code-generated-file-9b495122-4a9a-47a8-86f7-57b672ceb2ec]

이 프롬프트에는 카파시의 하네스 원칙을 적용하여, 환경 설정부터 명확한 모델링, pgvector 확장 활성화, 외래 키 제약 조건 및 관계 설정까지 상세하게 작업 지시를 내리도록 구성했습니다. 클로드에게 이 내용을 그대로 전달하여 작업을 시작하시면 됩니다.

```

---

## 4. 현재 스키마 (구현 완료) — RAG용 embedding 컬럼

위 프롬프트로 생성된 ORM(`adapter/outbound/orm/*.py`)과 Alembic 마이그레이션
(`minho/alembic/versions/20260713_0001_create_soccer_tables.py`)에는 `moneyball_players`
테이블에 pgvector `embedding` 컬럼이 이미 반영되어 있다.

| 테이블 | 컬럼 | 타입 | 설명 |
|---|---|---|---|
| `moneyball_players` | `embedding` | `vector(768)`, nullable | 선수 프로필(이름·포지션·국적 등) 기반 RAG 유사도 검색용. `EMBEDDING_DIM = 768`은 `community` 앱과 동일 규격. 값을 채우는 임베딩 파이프라인은 아직 없음 — 컬럼 구조만 미리 준비된 상태 |

- `stadium` / `team` / `schedule` 테이블에는 embedding 컬럼이 없다. RAG 대상은 현재 `player` 한 테이블로 한정.
- 마이그레이션은 `CREATE EXTENSION IF NOT EXISTS vector` 를 `upgrade()` 최상단에서 실행해 pgvector 확장을 보장한다.
- 임베딩을 채우려면: 선수 텍스트 필드(예: `player_name` + `position` + `nation` 조합)를 임베딩 모델에 통과시켜 `moneyball_players.embedding` 을 UPDATE 하면 되고, 스키마 변경은 필요 없다.