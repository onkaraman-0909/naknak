from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.security import get_password_hash


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create(
    db: Session,
    *,
    email: str,
    password: str,
    phone: str | None = None,
    locale: str | None = "tr",
) -> User:
    user = User(
        email=email,
        phone=phone,
        password_hash=get_password_hash(password),
        locale=locale,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()
