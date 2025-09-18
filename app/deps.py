from __future__ import annotations
from typing import Generator

from sqlalchemy.orm import Session

from .db import SessionLocal
from .config import settings


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_settings():
    return settings
