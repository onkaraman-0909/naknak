from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.crud import user as user_crud
from app.security import verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserOut:
    existing = user_crud.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-posta zaten kayıtlı")
    created = user_crud.create(
        db,
        email=payload.email,
        password=payload.password,
        phone=payload.phone,
        locale=payload.locale,
    )
    return created  # Pydantic from_attributes ile serialize edilir


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    u = user_crud.get_by_email(db, payload.email)
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kimlik bilgileri")
    access = create_access_token(str(u.id))
    refresh = create_refresh_token(str(u.id))
    return TokenResponse(access_token=access, refresh_token=refresh)
