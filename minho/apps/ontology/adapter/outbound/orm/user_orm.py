"""ontology_users — 사용자 엔티티 (pgvector 임베딩 컬럼 포함)."""

from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

EMBEDDING_DIM = 768


class UserOrm(Base):
    __tablename__ = "ontology_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    jobs: Mapped[list[JobOrm]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
