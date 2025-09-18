from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, PKMixin, TimestampMixin


class Offer(PKMixin, TimestampMixin, Base):
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle.id"), nullable=False, index=True
    )
    from_address_id: Mapped[int] = mapped_column(
        ForeignKey("address.id"), nullable=False
    )
    to_address_id: Mapped[int] = mapped_column(ForeignKey("address.id"), nullable=False)
    depart_date: Mapped[date] = mapped_column(Date, nullable=False)

    vehicle = relationship("Vehicle", backref="offers")
    from_address = relationship("Address", foreign_keys=[from_address_id])
    to_address = relationship("Address", foreign_keys=[to_address_id])
