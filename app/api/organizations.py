from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import org_user as org_user_crud
from app.crud import organization as org_crud
from app.deps import get_current_user, get_db, require_org_admin
from app.models.enums import OrgRole
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationOut,
    OrganizationUpdate,
)

router = APIRouter(prefix="/orgs", tags=["organizations"])


@router.get(
    "/", response_model=list[OrganizationOut], summary="Sahip olunan organizasyonlar"
)
def list_my_orgs(
    limit: int | None = None,
    offset: int | None = None,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    return org_crud.list_by_owner(db, me.id, limit=limit, offset=offset)


@router.post(
    "/",
    response_model=OrganizationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Organizasyon oluştur",
)
def create_org(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    org = org_crud.create(
        db,
        title=payload.title,
        owner_user_id=me.id,
        tax_office=payload.tax_office,
        tax_number=payload.tax_number,
    )
    # owner becomes corporate_admin by default
    org_user_crud.assign_role(
        db, organization_id=org.id, user_id=me.id, role=OrgRole.corporate_admin
    )
    return org


@router.get("/{org_id}", response_model=OrganizationOut, summary="Organizasyon detayı")
def get_org(
    org_id: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)
):
    org = org_crud.get(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organizasyon bulunamadı"
        )
    # izin: sahibi ya da admin olan görebilir, aksi halde 404
    if org.owner_user_id != me.id and not org_user_crud.is_admin(db, org_id, me.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organizasyon bulunamadı"
        )
    return org


@router.patch(
    "/{org_id}", response_model=OrganizationOut, summary="Organizasyon güncelle"
)
def update_org(
    org_id: int,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_org_admin),
):
    org = org_crud.get(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organizasyon bulunamadı"
        )
    return org_crud.update(
        db,
        org,
        title=payload.title,
        tax_office=payload.tax_office,
        tax_number=payload.tax_number,
    )


@router.delete(
    "/{org_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Organizasyon sil"
)
def delete_org(
    org_id: int, db: Session = Depends(get_db), _: bool = Depends(require_org_admin)
):
    org = org_crud.get(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organizasyon bulunamadı"
        )
    org_crud.delete(db, org)
    return None
