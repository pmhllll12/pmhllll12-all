from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ScheduleOrm(Base):
    __tablename__ = "schedule"

    sche_date: Mapped[str] = mapped_column(String(10), primary_key=True)
    stadium_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("stadium.stadium_id"), primary_key=True
    )
    gubun: Mapped[str | None] = mapped_column(String(10))
    hometeam_id: Mapped[str | None] = mapped_column(String(10), ForeignKey("team.team_id"))
    awayteam_id: Mapped[str | None] = mapped_column(String(10), ForeignKey("team.team_id"))
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)


__all__ = ["ScheduleOrm"]
