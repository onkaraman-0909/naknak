from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, PKMixin, TimestampMixin
from .enums import MatchStatusEnum, MatchStatus, CurrencyEnum, Currency


class Match(PKMixin, TimestampMixin, Base):
    load_id: Mapped[int] = mapped_column(ForeignKey("load.id"), nullable=False, index=True)
    offer_id: Mapped[int] = mapped_column(ForeignKey("offer.id"), nullable=False, index=True)

    status: Mapped[MatchStatus] = mapped_column(MatchStatusEnum, default=MatchStatus.pending, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    price: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currency: Mapped[Optional[Currency]] = mapped_column(CurrencyEnum)

    load = relationship("Load", backref="matches")
    offer = relationship("Offer", backref="matches")
