from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app.deps import get_current_user, get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.security import (
    create_access_token,
    create_refresh_token,
    get_subject_from_token,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserOut:
    existing = user_crud.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="E-posta zaten kayıtlı"
        )
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kimlik bilgileri"
        )
    access = create_access_token(str(u.id))
    refresh = create_refresh_token(str(u.id))
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest) -> TokenResponse:
    # verify refresh token and issue a new access/refresh pair
    user_id = get_subject_from_token(payload.refresh_token, expected_type="refresh")
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=UserOut)
def me(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    return current_user
