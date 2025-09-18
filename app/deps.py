from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session

from .config import settings
from .db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_settings():
    return settings
