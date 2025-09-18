from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle


def get(db: Session, vehicle_id: int) -> Optional[Vehicle]:
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def list_my(
    db: Session,
    owner_user_id: int,
    *,
    organization_id: Optional[int] = None,
    limit: int | None = None,
    offset: int | None = None,
) -> Sequence[Vehicle]:
    q = (
        db.query(Vehicle)
        .filter(Vehicle.owner_user_id == owner_user_id)
        .order_by(Vehicle.id.desc())
    )
    if organization_id is not None:
        q = q.filter(Vehicle.organization_id == organization_id)
    if offset:
        q = q.offset(offset)
    if limit:
        q = q.limit(limit)
    return q.all()


def create(
    db: Session,
    *,
    owner_user_id: int,
    organization_id: Optional[int] = None,
    capacity_value: Optional[float] = None,
    capacity_unit: Optional[str] = None,
    can_food: bool = False,
    can_dg: bool = False,
) -> Vehicle:
    v = Vehicle(
        owner_user_id=owner_user_id,
        organization_id=organization_id,
        capacity_value=capacity_value,
        capacity_unit=capacity_unit,
        can_food=can_food,
        can_dg=can_dg,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def update(
    db: Session,
    v: Vehicle,
    *,
    organization_id: Optional[int] = None,
    capacity_value: Optional[float] = None,
    capacity_unit: Optional[str] = None,
    can_food: Optional[bool] = None,
    can_dg: Optional[bool] = None,
) -> Vehicle:
    if organization_id is not None:
        v.organization_id = organization_id
    if capacity_value is not None:
        v.capacity_value = capacity_value
    if capacity_unit is not None:
        v.capacity_unit = capacity_unit
    if can_food is not None:
        v.can_food = can_food
    if can_dg is not None:
        v.can_dg = can_dg
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def delete(db: Session, v: Vehicle) -> None:
    db.delete(v)
    db.commit()
