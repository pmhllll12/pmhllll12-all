"""James CSV 업로드 등에서 쓰는 승객 ORM (`PersonOrm`)."""

from __future__ import annotations

from matrix.grid_neo_theone_base import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class PersonOrm(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    passenger_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    gender: Mapped[str] = mapped_column(String(32), nullable=False)
    age: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    sib_sp: Mapped[str] = mapped_column(String(16), nullable=False, default="0")
    parch: Mapped[str] = mapped_column(String(16), nullable=False, default="0")
    survived: Mapped[str] = mapped_column(String(8), nullable=False, default="0")


__all__ = ["PersonOrm"]
