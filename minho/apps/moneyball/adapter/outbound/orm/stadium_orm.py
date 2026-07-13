from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class StadiumOrm(Base):
    __tablename__ = "stadium"

    stadium_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    stadium_name: Mapped[str | None] = mapped_column(String(40))
    hometeam_id: Mapped[str | None] = mapped_column(String(10))
    seat_count: Mapped[int | None] = mapped_column(Integer)
    address: Mapped[str | None] = mapped_column(String(60))
    ddd: Mapped[str | None] = mapped_column(String(10))
    tel: Mapped[str | None] = mapped_column(String(10))


__all__ = ["StadiumOrm"]
