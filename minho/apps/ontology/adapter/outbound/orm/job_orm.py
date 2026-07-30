"""ontology_jobs — 직업 엔티티. userid 가 ontology_users.id 를 참조한다."""

from __future__ import annotations

from database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ontology.adapter.outbound.orm.user_orm import UserOrm

EMBEDDING_DIM = 768


class JobOrm(Base):
    __tablename__ = "ontology_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    company: Mapped[str] = mapped_column(String(100), nullable=False)
    userid: Mapped[int] = mapped_column(
        Integer, ForeignKey("ontology_users.id", ondelete="CASCADE"), nullable=False
    )
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    user: Mapped[UserOrm] = relationship(back_populates="jobs")
