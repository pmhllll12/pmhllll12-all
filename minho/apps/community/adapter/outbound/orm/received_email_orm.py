from __future__ import annotations

from datetime import datetime

from database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

EMBEDDING_DIM = 768


class ReceivedEmailOrm(Base):
    __tablename__ = "community_received_emails"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject: Mapped[str] = mapped_column(String(500), default="")
    from_email: Mapped[str] = mapped_column(String(320), default="", index=True)
    to_email: Mapped[str] = mapped_column(String(320), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
    message_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
