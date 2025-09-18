from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import load as load_crud
from app.crud import org_user as org_user_crud
from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.load import LoadCreate, LoadOut, LoadUpdate

router = APIRouter(prefix="/loads", tags=["loads"])


@router.get("/", response_model=list[LoadOut], summary="Kullanıcının yükleri")
def list_my_loads(
    organization_id: int | None = None,
    limit: int | None = None,
    offset: int | None = None,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    return load_crud.list_my(
        db,
        me.id,
        organization_id=organization_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/",
    response_model=LoadOut,
    status_code=status.HTTP_201_CREATED,
    summary="Yük oluştur",
)
def create_load(
    payload: LoadCreate,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    # Eğer organization_id verildiyse: sadece ilgili organizasyon adminleri yük oluşturabilir
    if payload.organization_id is not None:
        if not org_user_crud.is_admin(db, payload.organization_id, me.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Yetki yok (organization admin gerekli)",
            )
    return load_crud.create(
        db,
        owner_user_id=me.id,
        organization_id=payload.organization_id,
        name=payload.name,
        quantity_value=payload.quantity_value,
        quantity_unit=payload.quantity_unit,
        category=payload.category,
        pickup_address_id=payload.pickup_address_id,
        dropoff_address_id=payload.dropoff_address_id,
        pickup_day=payload.pickup_day,
        intl=payload.intl,
    )


@router.get("/{load_id}", response_model=LoadOut, summary="Yük detayı")
def get_load(
    load_id: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)
):
    load_obj = load_crud.get(db, load_id)
    if not load_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Yük bulunamadı"
        )
    # İzin: sahibi görebilir; org'a bağlı ise org admini de görebilir
    if load_obj.owner_user_id is not None and load_obj.owner_user_id == me.id:
        return load_obj
    if load_obj.organization_id is not None and org_user_crud.is_admin(
        db, load_obj.organization_id, me.id
    ):
        return load_obj
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yük bulunamadı")


@router.patch("/{load_id}", response_model=LoadOut, summary="Yük güncelle")
def update_load(
    load_id: int,
    payload: LoadUpdate,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    load_obj = load_crud.get(db, load_id)
    if not load_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Yük bulunamadı"
        )
    authorized = load_obj.owner_user_id == me.id or (
        load_obj.organization_id is not None
        and org_user_crud.is_admin(db, load_obj.organization_id, me.id)
    )
    if not authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yetki yok")
    return load_crud.update(
        db,
        load_obj,
        organization_id=payload.organization_id,
        name=payload.name,
        quantity_value=payload.quantity_value,
        quantity_unit=payload.quantity_unit,
        category=payload.category,
        pickup_address_id=payload.pickup_address_id,
        dropoff_address_id=payload.dropoff_address_id,
        pickup_day=payload.pickup_day,
        intl=payload.intl,
    )


@router.delete("/{load_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Yük sil")
def delete_load(
    load_id: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)
):
    load_obj = load_crud.get(db, load_id)
    if not load_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Yük bulunamadı"
        )
    authorized = load_obj.owner_user_id == me.id or (
        load_obj.organization_id is not None
        and org_user_crud.is_admin(db, load_obj.organization_id, me.id)
    )
    if not authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yetki yok")
    load_crud.delete(db, load_obj)
    return None
