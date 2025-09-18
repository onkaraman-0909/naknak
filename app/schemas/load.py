from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Category, Unit


class LoadBase(BaseModel):
    organization_id: int | None = None
    name: str = Field(min_length=2, max_length=100)
    quantity_value: float | None = Field(default=None, ge=0)
    quantity_unit: Unit | None = None
    category: Category | None = None
    pickup_address_id: int
    dropoff_address_id: int
    pickup_day: date
    intl: bool = False


class LoadCreate(LoadBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "organization_id": 1,
                "name": "Gıda kolisi",
                "quantity_value": 500,
                "quantity_unit": "KG",
                "category": "GIDA",
                "pickup_address_id": 1,
                "dropoff_address_id": 2,
                "pickup_day": "2025-12-31",
                "intl": False,
            }
        }
    )


class LoadUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    organization_id: int | None = None
    quantity_value: float | None = Field(default=None, ge=0)
    quantity_unit: Unit | None = None
    category: Category | None = None
    pickup_address_id: int | None = None
    dropoff_address_id: int | None = None
    pickup_day: date | None = None
    intl: bool | None = None


class LoadOut(LoadBase):
    id: int
    owner_user_id: int | None = None
    model_config = ConfigDict(from_attributes=True)
