from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.models.load import Load


def get(db: Session, load_id: int) -> Optional[Load]:
    return db.query(Load).filter(Load.id == load_id).first()


def list_my(
    db: Session,
    owner_user_id: int,
    *,
    organization_id: Optional[int] = None,
    limit: int | None = None,
    offset: int | None = None,
) -> Sequence[Load]:
    q = (
        db.query(Load)
        .filter(Load.owner_user_id == owner_user_id)
        .order_by(Load.id.desc())
    )
    if organization_id is not None:
        q = q.filter(Load.organization_id == organization_id)
    if offset:
        q = q.offset(offset)
    if limit:
        q = q.limit(limit)
    return q.all()


def create(
    db: Session,
    *,
    owner_user_id: int,
    organization_id: Optional[int],
    name: str,
    quantity_value: Optional[float],
    quantity_unit: Optional[str],
    category: Optional[str],
    pickup_address_id: int,
    dropoff_address_id: int,
    pickup_day,
    intl: bool,
) -> Load:
    load_obj = Load(
        owner_user_id=owner_user_id,
        organization_id=organization_id,
        name=name,
        quantity_value=quantity_value,
        quantity_unit=quantity_unit,
        category=category,
        pickup_address_id=pickup_address_id,
        dropoff_address_id=dropoff_address_id,
        pickup_day=pickup_day,
        intl=intl,
    )
    db.add(load_obj)
    db.commit()
    db.refresh(load_obj)
    return load_obj


def update(
    db: Session,
    load_obj: Load,
    *,
    organization_id: Optional[int] = None,
    name: Optional[str] = None,
    quantity_value: Optional[float] = None,
    quantity_unit: Optional[str] = None,
    category: Optional[str] = None,
    pickup_address_id: Optional[int] = None,
    dropoff_address_id: Optional[int] = None,
    pickup_day=None,
    intl: Optional[bool] = None,
) -> Load:
    if organization_id is not None:
        load_obj.organization_id = organization_id
    if name is not None:
        load_obj.name = name
    if quantity_value is not None:
        load_obj.quantity_value = quantity_value
    if quantity_unit is not None:
        load_obj.quantity_unit = quantity_unit
    if category is not None:
        load_obj.category = category
    if pickup_address_id is not None:
        load_obj.pickup_address_id = pickup_address_id
    if dropoff_address_id is not None:
        load_obj.dropoff_address_id = dropoff_address_id
    if pickup_day is not None:
        load_obj.pickup_day = pickup_day
    if intl is not None:
        load_obj.intl = intl
    db.add(load_obj)
    db.commit()
    db.refresh(load_obj)
    return load_obj


def delete(db: Session, load_obj: Load) -> None:
    db.delete(load_obj)
    db.commit()
