from __future__ import annotations
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, PKMixin, TimestampMixin


class Address(PKMixin, TimestampMixin, Base):
    country: Mapped[str] = mapped_column(String(2), nullable=False, doc="ISO country code, e.g., TR")
    admin1: Mapped[Optional[str]] = mapped_column(String(128), doc="İl / State / Province")
    admin2: Mapped[Optional[str]] = mapped_column(String(128), doc="İlçe / County")
    admin3: Mapped[Optional[str]] = mapped_column(String(128), doc="Mahalle / Subdistrict")
    line_optional: Mapped[Optional[str]] = mapped_column(String(255), doc="Ek adres satırı (opsiyonel)")
