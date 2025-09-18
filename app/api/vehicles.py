from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import org_user as org_user_crud
from app.crud import vehicle as vehicle_crud
from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehicleUpdate

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/", response_model=list[VehicleOut], summary="Kullanıcının araçları")
def list_my_vehicles(
    organization_id: int | None = None,
    limit: int | None = None,
    offset: int | None = None,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    return vehicle_crud.list_my(
        db,
        me.id,
        organization_id=organization_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/",
    response_model=VehicleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Araç oluştur",
)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    # Eğer organization_id verildiyse: sadece ilgili organizasyon adminleri oluşturabilir
    if payload.organization_id is not None:
        if not org_user_crud.is_admin(db, payload.organization_id, me.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Yetki yok (organization admin gerekli)",
            )
    return vehicle_crud.create(
        db,
        owner_user_id=me.id,
        organization_id=payload.organization_id,
        capacity_value=payload.capacity_value,
        capacity_unit=payload.capacity_unit,
        can_food=payload.can_food,
        can_dg=payload.can_dg,
    )


@router.get("/{vehicle_id}", response_model=VehicleOut, summary="Araç detayı")
def get_vehicle(
    vehicle_id: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)
):
    v = vehicle_crud.get(db, vehicle_id)
    if not v:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Araç bulunamadı"
        )
    # İzin: sahibi görebilir. Eğer org'a bağlıysa ilgili org admini de görebilir.
    if v.owner_user_id is not None and v.owner_user_id == me.id:
        return v
    if v.organization_id is not None and org_user_crud.is_admin(
        db, v.organization_id, me.id
    ):
        return v
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Araç bulunamadı")


@router.patch("/{vehicle_id}", response_model=VehicleOut, summary="Araç güncelle")
def update_vehicle(
    vehicle_id: int,
    payload: VehicleUpdate,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    v = vehicle_crud.get(db, vehicle_id)
    if not v:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Araç bulunamadı"
        )
    # İzin: sahibi güncelleyebilir; org'a bağlı ise org admini de güncelleyebilir
    authorized = v.owner_user_id == me.id or (
        v.organization_id is not None
        and org_user_crud.is_admin(db, v.organization_id, me.id)
    )
    if not authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yetki yok")
    return vehicle_crud.update(
        db,
        v,
        organization_id=payload.organization_id,
        capacity_value=payload.capacity_value,
        capacity_unit=payload.capacity_unit,
        can_food=payload.can_food,
        can_dg=payload.can_dg,
    )


@router.delete(
    "/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Araç sil"
)
def delete_vehicle(
    vehicle_id: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)
):
    v = vehicle_crud.get(db, vehicle_id)
    if not v:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Araç bulunamadı"
        )
    authorized = v.owner_user_id == me.id or (
        v.organization_id is not None
        and org_user_crud.is_admin(db, v.organization_id, me.id)
    )
    if not authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yetki yok")
    vehicle_crud.delete(db, v)
    return None
