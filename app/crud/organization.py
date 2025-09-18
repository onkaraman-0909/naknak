from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.models.organization import Organization


def get(db: Session, org_id: int) -> Optional[Organization]:
    return db.query(Organization).filter(Organization.id == org_id).first()


def list_by_owner(
    db: Session,
    owner_user_id: int,
    *,
    limit: int | None = None,
    offset: int | None = None,
) -> Sequence[Organization]:
    q = (
        db.query(Organization)
        .filter(Organization.owner_user_id == owner_user_id)
        .order_by(Organization.id.desc())
    )
    if offset:
        q = q.offset(offset)
    if limit:
        q = q.limit(limit)
    return q.all()


def create(
    db: Session,
    *,
    title: str,
    owner_user_id: int,
    tax_office: Optional[str] = None,
    tax_number: Optional[str] = None,
) -> Organization:
    org = Organization(
        title=title,
        owner_user_id=owner_user_id,
        tax_office=tax_office,
        tax_number=tax_number,
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def update(
    db: Session,
    org: Organization,
    *,
    title: Optional[str] = None,
    tax_office: Optional[str] = None,
    tax_number: Optional[str] = None,
) -> Organization:
    if title is not None:
        org.title = title
    if tax_office is not None:
        org.tax_office = tax_office
    if tax_number is not None:
        org.tax_number = tax_number
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def delete(db: Session, org: Organization) -> None:
    db.delete(org)
    db.commit()
