from __future__ import annotations
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, PKMixin, TimestampMixin
from .enums import StatusEnum, GenericStatus


class Organization(PKMixin, TimestampMixin, Base):
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_office: Mapped[Optional[str]] = mapped_column(String(128))
    tax_number: Mapped[Optional[str]] = mapped_column(String(16), index=True)
    address_id: Mapped[Optional[int]] = mapped_column(ForeignKey("address.id"))
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    status: Mapped[GenericStatus] = mapped_column(StatusEnum, default=GenericStatus.active, nullable=False)

    owner = relationship("User", backref="owned_organizations")
    users = relationship("OrgUser", back_populates="organization", cascade="all, delete-orphan")
