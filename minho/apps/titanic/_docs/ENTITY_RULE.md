# 엔티티·테이블 규칙 — 기본 키 `id` (정수, 자동 증가)

## 원칙

- 이 프로젝트의 **모든 테이블**은 **정수(`int`)** 타입의 **내부용 자동 증가 고유 번호**를 기본 키(Primary Key)로 둔다.
- DB 컬럼명·ORM 속성명을 **`id`로 통일**한다. (`user_id`, `order_no` 등 비즈니스 식별자는 **별도 컬럼**으로 두고, PK 이름은 `id`만 사용한다.)

---

## 1. SQLModel 사용 시 (참조 패턴)

시스템 내부용 자동 증감 PK는 아래와 같이 정의한다.

```python
from typing import Optional

from sqlmodel import Field, SQLModel


class ExampleEntity(SQLModel, table=True):
    __tablename__ = "example_table"

    # 시스템 내부용 자동 증감 고유 번호 (기본 키)
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"name": "id"},  # DB 컬럼명: id
    )
    # 이하 비즈니스 컬럼…
```

- `default=None`: INSERT 시 DB가 시퀀스/자동 증가로 채우도록 두는 일반적인 패턴이다.
- `primary_key=True`: 기본 키 지정.
- `sa_column_kwargs={"name": "id"}`: SQLAlchemy 레벨에서 컬럼 물리명이 **`id`**임을 명시한다(매핑 클래스 속성명과 일치시키는 용도).

> Alembic 마이그레이션·`CREATE TABLE`을 쓸 때도 PK 컬럼명은 **`id`**, 타입은 **`INTEGER`**(또는 DB에 맞는 정수) + **`AUTO_INCREMENT` / `SERIAL` / `IDENTITY`** 등 프로젝트 표준에 맞게 생성한다.

---

## 2. SQLAlchemy 2.0 Declarative (`Mapped`) 사용 시 — 이 저장소 예시

`backend/apps` 일부 모듈은 `database.Base` + `Mapped` / `mapped_column`을 쓴다. 동일 규칙은 다음과 같다.

```python
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(Base):
    __tablename__ = "secom_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 이하 비즈니스 컬럼…
```

- PK는 **`id`**, 타입 **`int`**, **`autoincrement=True`**(또는 DB dialect에 맞는 정수 자동 증가).
- 비즈니스 키(로그인 아이디, 이메일 등)는 **`id`와 혼동되지 않는 컬럼명**으로 둔다.

---

## 3. 하지 말 것

| 하지 말기 | 이유 |
|-----------|------|
| 문자열 UUID만 PK로 두고 `id` 없음 | 프로젝트 표준과 불일치(별도 `id` int PK 유지). |
| PK 컬럼명을 `pk`, `idx`, 테이블명 접두 등으로 분산 | **`id`로 통일**해야 조인·관례·도구가 단순해진다. |
| 비즈니스 식별자(`email`, `user_id`)를 PK로만 쓰고 내부 `id` 생략 | 변경·이관·참조 안정성을 위해 **내부 정수 PK `id`**를 둔다. |

---

## 4. 체크리스트 (새 테이블·엔티티 추가 시)

1. [ ] PK 컬럼명이 **`id`**인가?
2. [ ] 타입이 **정수**이고 **자동 증가**(또는 DB 시퀀스)인가?
3. [ ] 대외·도메인 식별자는 **`id`가 아닌 별도 컬럼**에 있는가?

---

*이 문서를 바꿀 때는 실제 `backend/apps` 모델 예시(`secom` 등)와 충돌이 없는지 함께 확인한다.*
