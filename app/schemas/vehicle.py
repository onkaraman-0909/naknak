from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Unit


class VehicleBase(BaseModel):
    organization_id: int | None = None
    capacity_value: float | None = Field(default=None, ge=0)
    capacity_unit: Unit | None = None
    can_food: bool = False
    can_dg: bool = False


class VehicleCreate(VehicleBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "organization_id": 1,
                "capacity_value": 12000,
                "capacity_unit": "KG",
                "can_food": True,
                "can_dg": False,
            }
        }
    )


class VehicleUpdate(BaseModel):
    organization_id: int | None = None
    capacity_value: float | None = Field(default=None, ge=0)
    capacity_unit: Unit | None = None
    can_food: bool | None = None
    can_dg: bool | None = None


class VehicleOut(VehicleBase):
    id: int
    owner_user_id: int | None = None
    model_config = ConfigDict(from_attributes=True)
