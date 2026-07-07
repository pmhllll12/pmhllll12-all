"""James CSV 업로드 등에서 쓰는 예약 ORM (`BookingOrm`)."""

from __future__ import annotations

from matrix.grid_neo_theone_base import Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class BookingOrm(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("persons.id"), nullable=False)
    pclass: Mapped[str] = mapped_column(String(8), nullable=False)
    ticket: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    fare: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    cabin: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    embarked: Mapped[str] = mapped_column(String(8), nullable=False, default="")


__all__ = ["BookingOrm"]
