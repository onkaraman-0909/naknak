from __future__ import annotations
from enum import Enum

from sqlalchemy import Enum as SAEnum


class Unit(str, Enum):
    KG = "KG"
    TON = "TON"
    LITRE = "LITRE"


class Category(str, Enum):
    GIDA = "GIDA"
    TEHLIKELI = "TEHLIKELI"
    GENEL = "GENEL"


# Yardımcı: SQLAlchemy Enum tipini kolay kullanmak için
UnitEnum = SAEnum(Unit, name="unit_enum")
CategoryEnum = SAEnum(Category, name="category_enum")


class OrgRole(str, Enum):
    corporate_admin = "corporate_admin"
    corporate_user = "corporate_user"


class GenericStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


OrgRoleEnum = SAEnum(OrgRole, name="org_role_enum")
StatusEnum = SAEnum(GenericStatus, name="generic_status_enum")


class MatchStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"


class MembershipPlan(str, Enum):
    free = "free"
    pro = "pro"
    business = "business"


class Currency(str, Enum):
    TRY = "TRY"
    USD = "USD"
    EUR = "EUR"


MatchStatusEnum = SAEnum(MatchStatus, name="match_status_enum")
MembershipPlanEnum = SAEnum(MembershipPlan, name="membership_plan_enum")
CurrencyEnum = SAEnum(Currency, name="currency_enum")
