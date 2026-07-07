from __future__ import annotations

from database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class JusoContactOrm(Base):
    __tablename__ = "community_juso_contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), default="")
    middle_name: Mapped[str] = mapped_column(String(100), default="")
    last_name: Mapped[str] = mapped_column(String(100), default="")
    nickname: Mapped[str] = mapped_column(String(100), default="")
    organization_name: Mapped[str] = mapped_column(String(200), default="")
    organization_title: Mapped[str] = mapped_column(String(200), default="")
    email_1_value: Mapped[str] = mapped_column(String(255), default="", index=True)
    phone_1_value: Mapped[str] = mapped_column(String(50), default="")
    phone_2_value: Mapped[str] = mapped_column(String(50), default="")
    address_1_city: Mapped[str] = mapped_column(String(100), default="")
    address_1_country: Mapped[str] = mapped_column(String(100), default="")
    birthday: Mapped[str] = mapped_column(String(20), default="")
    labels: Mapped[str] = mapped_column(String(500), default="")
