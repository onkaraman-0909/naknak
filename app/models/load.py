from __future__ import annotations
from typing import Optional
from datetime import date
from sqlalchemy import ForeignKey, String, Boolean, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, PKMixin, TimestampMixin
from .enums import UnitEnum, CategoryEnum


class Load(PKMixin, TimestampMixin, Base):
    owner_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organization.id"), index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    quantity_value: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    quantity_unit = mapped_column(UnitEnum, nullable=True)

    category = mapped_column(CategoryEnum, nullable=True)

    pickup_address_id: Mapped[int] = mapped_column(ForeignKey("address.id"), nullable=False)
    dropoff_address_id: Mapped[int] = mapped_column(ForeignKey("address.id"), nullable=False)

    pickup_day: Mapped[date] = mapped_column(Date, nullable=False)
    intl: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    owner_user = relationship("User", backref="loads")
    organization = relationship("Organization", backref="loads")
    pickup_address = relationship("Address", foreign_keys=[pickup_address_id])
    dropoff_address = relationship("Address", foreign_keys=[dropoff_address_id])
