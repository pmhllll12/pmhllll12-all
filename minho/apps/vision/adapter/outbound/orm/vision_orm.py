from __future__ import annotations

from datetime import datetime

from sqlalchemy import ARRAY, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class AnalyzedImageOrm(Base):
    __tablename__ = "vision_analyzed_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(500), default="")
    caption: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(100)), default=list)
    image_key: Mapped[str] = mapped_column(String(1024), default="")
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
