from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class PlayerOrm(Base):
    __tablename__ = "player"

    player_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    player_name: Mapped[str | None] = mapped_column(String(20))
    e_player_name: Mapped[str | None] = mapped_column(String(40))
    nickname: Mapped[str | None] = mapped_column(String(30))
    join_yyyy: Mapped[str | None] = mapped_column(String(10))
    position: Mapped[str | None] = mapped_column(String(10))
    back_no: Mapped[int | None] = mapped_column(Integer)
    nation: Mapped[str | None] = mapped_column(String(20))
    birth_date: Mapped[date | None] = mapped_column(Date)
    solar: Mapped[str | None] = mapped_column(String(10))
    height: Mapped[int | None] = mapped_column(Integer)
    weight: Mapped[int | None] = mapped_column(Integer)
    team_id: Mapped[str | None] = mapped_column(String(10), ForeignKey("team.team_id"))


__all__ = ["PlayerOrm"]
