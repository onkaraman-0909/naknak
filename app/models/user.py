from __future__ import annotations
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, PKMixin, TimestampMixin
from .enums import StatusEnum, GenericStatus


class User(PKMixin, TimestampMixin, Base):
    # __tablename__ = "user"  # Base ile tekil otomatik

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    locale: Mapped[Optional[str]] = mapped_column(String(8), default="tr")
    status: Mapped[GenericStatus] = mapped_column(StatusEnum, default=GenericStatus.active, nullable=False)

    # ilişkiler (ileride kullanılacak)
    organizations = relationship("OrgUser", back_populates="user", cascade="all, delete-orphan")
