from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.enums import GenericStatus, OrgRole
from app.models.org_user import OrgUser


def get_link(db: Session, organization_id: int, user_id: int) -> Optional[OrgUser]:
    return (
        db.query(OrgUser)
        .filter(OrgUser.organization_id == organization_id, OrgUser.user_id == user_id)
        .first()
    )


def assign_role(
    db: Session,
    *,
    organization_id: int,
    user_id: int,
    role: OrgRole = OrgRole.corporate_user,
    status: GenericStatus = GenericStatus.active,
) -> OrgUser:
    link = get_link(db, organization_id, user_id)
    if link is None:
        link = OrgUser(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
            status=status,
        )
        db.add(link)
    else:
        link.role = role
        link.status = status
        db.add(link)
    db.commit()
    db.refresh(link)
    return link


def is_admin(db: Session, organization_id: int, user_id: int) -> bool:
    link = get_link(db, organization_id, user_id)
    return bool(
        link
        and link.role == OrgRole.corporate_admin
        and link.status == GenericStatus.active
    )
