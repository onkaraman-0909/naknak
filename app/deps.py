from __future__ import annotations

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from .crud import org_user as org_user_crud
from .crud import user as user_crud
from .db import SessionLocal
from .security import get_subject_from_token


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_settings():
    return settings


# OAuth2 bearer token reader for protected endpoints
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        subject = get_subject_from_token(token, expected_type="access")
        user_id = int(subject)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya süresi dolmuş token",
        )

    u = user_crud.get(db, user_id)
    if not u:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı"
        )
    return u


def require_org_admin(
    org_id: int,
    db: Session = Depends(get_db),
    me=Depends(get_current_user),
):
    """Raise 403 if current user is not admin of given organization.
    Returns True if authorized (value itself is unused by endpoints).
    """
    if not org_user_crud.is_admin(db, org_id, me.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yetki yok (organization admin gerekli)",
        )
    return True
