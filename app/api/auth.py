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


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kullanıcı kaydı",
    description="E-posta ve parola ile yeni kullanıcı oluşturur. E-posta benzersiz olmalıdır.",
    responses={
        400: {
            "description": "E-posta zaten kayıtlı",
            "content": {
                "application/json": {"example": {"detail": "E-posta zaten kayıtlı"}}
            },
        }
    },
)
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


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Kullanıcı girişi",
    description="Geçerli kimlik bilgileri ile access ve refresh token üretir.",
    responses={
        401: {
            "description": "Geçersiz kimlik bilgileri",
            "content": {
                "application/json": {"example": {"detail": "Geçersiz kimlik bilgileri"}}
            },
        }
    },
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    u = user_crud.get_by_email(db, payload.email)
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kimlik bilgileri"
        )
    access = create_access_token(str(u.id))
    refresh = create_refresh_token(str(u.id))
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Token yenileme",
    description="Geçerli bir refresh token verildiğinde yeni access ve refresh token çifti döner.",
    responses={
        401: {
            "description": "Geçersiz veya süresi dolmuş token",
            "content": {
                "application/json": {
                    "example": {"detail": "Geçersiz veya süresi dolmuş token"}
                }
            },
        }
    },
)
def refresh(payload: RefreshRequest) -> TokenResponse:
    # verify refresh token and issue a new access/refresh pair
    user_id = get_subject_from_token(payload.refresh_token, expected_type="refresh")
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Oturum açan kullanıcı bilgisi",
    description="Bearer access token ile kimliği doğrulanmış kullanıcının temel bilgilerini döner.",
    responses={
        401: {
            "description": "Yetkisiz",
            "content": {
                "application/json": {
                    "example": {"detail": "Geçersiz veya süresi dolmuş token"}
                }
            },
        }
    },
)
def me(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    return current_user
