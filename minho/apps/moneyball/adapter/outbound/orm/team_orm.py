from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TeamOrm(Base):
    __tablename__ = "team"

    team_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    region_name: Mapped[str | None] = mapped_column(String(10))
    team_name: Mapped[str | None] = mapped_column(String(40))
    e_team_name: Mapped[str | None] = mapped_column(String(50))
    orig_yyyy: Mapped[str | None] = mapped_column(String(10))
    zip_code1: Mapped[str | None] = mapped_column(String(10))
    zip_code2: Mapped[str | None] = mapped_column(String(10))
    address: Mapped[str | None] = mapped_column(String(80))
    ddd: Mapped[str | None] = mapped_column(String(10))
    tel: Mapped[str | None] = mapped_column(String(10))
    fax: Mapped[str | None] = mapped_column(String(10))
    homepage: Mapped[str | None] = mapped_column(String(50))
    owner: Mapped[str | None] = mapped_column(String(10))
    stadium_id: Mapped[str | None] = mapped_column(String(10), ForeignKey("stadium.stadium_id"))


__all__ = ["TeamOrm"]
