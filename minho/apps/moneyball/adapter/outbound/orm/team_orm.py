from __future__ import annotations

from database import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class TeamOrm(Base):
    __tablename__ = "moneyball_teams"

    team_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    region_name: Mapped[str | None] = mapped_column(String(10), nullable=True)
    team_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    e_team_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    orig_yyyy: Mapped[str | None] = mapped_column(String(10), nullable=True)
    zip_code1: Mapped[str | None] = mapped_column(String(10), nullable=True)
    zip_code2: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(String(80), nullable=True)
    ddd: Mapped[str | None] = mapped_column(String(10), nullable=True)
    tel: Mapped[str | None] = mapped_column(String(10), nullable=True)
    fax: Mapped[str | None] = mapped_column(String(10), nullable=True)
    homepage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(10), nullable=True)
    stadium_id: Mapped[str | None] = mapped_column(
        String(10), ForeignKey("moneyball_stadiums.stadium_id"), nullable=True
    )

    stadium: Mapped["StadiumOrm | None"] = relationship(back_populates="teams")  # noqa: F821
    players: Mapped[list["PlayerOrm"]] = relationship(back_populates="team")  # noqa: F821


__all__ = ["TeamOrm"]
