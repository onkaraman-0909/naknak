from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrganizationBase(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    tax_office: str | None = Field(default=None, max_length=128)
    tax_number: str | None = Field(default=None, max_length=16)


class OrganizationCreate(OrganizationBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "F4ST Lojistik A.Ş.",
                "tax_office": "Kadıköy",
                "tax_number": "1234567890",
            }
        }
    )


class OrganizationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    tax_office: str | None = Field(default=None, max_length=128)
    tax_number: str | None = Field(default=None, max_length=16)


class OrganizationOut(OrganizationBase):
    id: int
    owner_user_id: int
    model_config = ConfigDict(from_attributes=True)
