from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, PKMixin, TimestampMixin


class Rating(PKMixin, TimestampMixin, Base):
    rater_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, index=True
    )
    ratee_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, index=True
    )
    match_id: Mapped[int] = mapped_column(
        ForeignKey("match.id"), nullable=False, index=True
    )

    q1: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    q2: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    q3: Mapped[Optional[int]] = mapped_column(SmallInteger)
    q4: Mapped[Optional[int]] = mapped_column(SmallInteger)
    overall: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    rater = relationship("User", foreign_keys=[rater_user_id])
    ratee = relationship("User", foreign_keys=[ratee_user_id])
    match = relationship("Match", backref="ratings")
