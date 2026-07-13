from __future__ import annotations

from database import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class StadiumOrm(Base):
    __tablename__ = "moneyball_stadiums"

    stadium_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    # ERD 원본 컬럼명의 오탈자(statdium_name)를 그대로 유지 — 소스 데이터셋 적재 시
    # 컬럼명이 어긋나지 않도록 임의로 고치지 않는다.
    statdium_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    hometeam_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    seat_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    address: Mapped[str | None] = mapped_column(String(60), nullable=True)
    ddd: Mapped[str | None] = mapped_column(String(10), nullable=True)
    tel: Mapped[str | None] = mapped_column(String(10), nullable=True)

    teams: Mapped[list["TeamOrm"]] = relationship(back_populates="stadium")  # noqa: F821
    schedules: Mapped[list["ScheduleOrm"]] = relationship(back_populates="stadium")  # noqa: F821


__all__ = ["StadiumOrm"]
