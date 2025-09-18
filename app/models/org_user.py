from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, PKMixin, TimestampMixin
from .enums import GenericStatus, OrgRole, OrgRoleEnum, StatusEnum


class OrgUser(PKMixin, TimestampMixin, Base):
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organization.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, index=True
    )
    role: Mapped[OrgRole] = mapped_column(
        OrgRoleEnum, default=OrgRole.corporate_user, nullable=False
    )
    status: Mapped[GenericStatus] = mapped_column(
        StatusEnum, default=GenericStatus.active, nullable=False
    )

    organization = relationship("Organization", back_populates="users")
    user = relationship("User", back_populates="organizations")
