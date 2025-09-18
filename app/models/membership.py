from __future__ import annotations
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, PKMixin, TimestampMixin
from .enums import MembershipPlanEnum, MembershipPlan, StatusEnum, GenericStatus


class Membership(PKMixin, TimestampMixin, Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)

    plan: Mapped[MembershipPlan] = mapped_column(MembershipPlanEnum, nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    priority_score: Mapped[int] = mapped_column(default=0, nullable=False)
    status: Mapped[GenericStatus] = mapped_column(StatusEnum, default=GenericStatus.active, nullable=False)

    user = relationship("User", backref="memberships")
