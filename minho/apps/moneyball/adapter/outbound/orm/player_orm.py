from __future__ import annotations

from datetime import date

from database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

# 선수 스카우팅 유사도 검색(향후 기능)을 위한 임베딩 차원 — community 앱과 동일 규격
EMBEDDING_DIM = 768


class PlayerOrm(Base):
    __tablename__ = "moneyball_players"

    player_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    player_name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    e_player_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(30), nullable=True)
    join_yyyy: Mapped[str | None] = mapped_column(String(10), nullable=True)
    position: Mapped[str | None] = mapped_column(String(10), nullable=True)
    back_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(nullable=True)
    solar: Mapped[str | None] = mapped_column(String(10), nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True)
    team_id: Mapped[str | None] = mapped_column(
        String(10), ForeignKey("moneyball_teams.team_id"), nullable=True
    )
    # 아직 값을 채우는 파이프라인은 없음 — pgvector 유사도 검색이 필요해지면
    # 이 컬럼에 임베딩을 채워 넣기만 하면 되도록 구조만 미리 마련해 둔다.
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    team: Mapped["TeamOrm | None"] = relationship(back_populates="players")  # noqa: F821


__all__ = ["PlayerOrm"]
