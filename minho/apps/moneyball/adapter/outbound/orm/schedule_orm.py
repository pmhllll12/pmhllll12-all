from __future__ import annotations

from database import Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ScheduleOrm(Base):
    __tablename__ = "moneyball_schedules"

    # ERD상 sche_date + stadium_id 복합 기본키 (동일 구장에서 날짜별로 유일)
    sche_date: Mapped[str] = mapped_column(String(10), primary_key=True)
    stadium_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("moneyball_stadiums.stadium_id"), primary_key=True
    )
    gubun: Mapped[str | None] = mapped_column(String(10), nullable=True)
    hometeam_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    awayteam_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    stadium: Mapped["StadiumOrm"] = relationship(back_populates="schedules")  # noqa: F821


__all__ = ["ScheduleOrm"]
