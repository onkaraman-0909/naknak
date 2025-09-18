from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    phone: str | None = None
    locale: str | None = "tr"
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "secret123",
                "phone": "+905551112233",
                "locale": "tr",
            }
        }
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "secret123",
            }
        }
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "<jwt-access>",
                "refresh_token": "<jwt-refresh>",
                "token_type": "bearer",
            }
        }
    )


class UserOut(BaseModel):
    id: int
    email: EmailStr
    phone: str | None
    locale: str | None
    # Pydantic v2: use ConfigDict instead of inner Config
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "phone": "+905551112233",
                "locale": "tr",
            }
        },
    )


class RefreshRequest(BaseModel):
    refresh_token: str
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "<jwt-refresh>",
            }
        }
    )
