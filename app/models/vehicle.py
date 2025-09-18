from __future__ import annotations
from typing import Optional
from sqlalchemy import ForeignKey, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, PKMixin, TimestampMixin
from .enums import UnitEnum, StatusEnum, GenericStatus


class Vehicle(PKMixin, TimestampMixin, Base):
    owner_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organization.id"), index=True)

    capacity_value: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    capacity_unit = mapped_column(UnitEnum, nullable=True)

    can_food: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_dg: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    status: Mapped[GenericStatus] = mapped_column(StatusEnum, default=GenericStatus.active, nullable=False)

    owner_user = relationship("User", backref="vehicles")
    organization = relationship("Organization", backref="vehicles")
