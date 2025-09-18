from contextlib import contextmanager
from typing import Generator

from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.crud import org_user as org_user_crud
from app.deps import get_db
from app.main import app

# ensure models registered
from app.models import address as _address  # noqa: F401
from app.models import load as _load  # noqa: F401
from app.models import organization as _organization  # noqa: F401
from app.models import user as _user  # noqa: F401
from app.models.base import Base
from app.models.enums import OrgRole

TESTING_SESSION_LOCAL: sessionmaker | None = None


def _setup_test_db():
    global TESTING_SESSION_LOCAL
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TESTING_SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    @contextmanager
    def _session_scope() -> Generator[Session, None, None]:
        db = TESTING_SESSION_LOCAL()  # type: ignore[operator]
        try:
            yield db
            db.commit()
        finally:
            db.close()

    def override_get_db() -> Generator[Session, None, None]:
        with _session_scope() as s:
            yield s

    return override_get_db


def _create_address(
    country="TR", admin1="IST", admin2="KADIKOY", admin3=None, line_optional=None
) -> int:
    assert TESTING_SESSION_LOCAL is not None
    with TESTING_SESSION_LOCAL() as db:  # type: ignore[operator]
        from app.models.address import Address

        addr = Address(
            country=country,
            admin1=admin1,
            admin2=admin2,
            admin3=admin3,
            line_optional=line_optional,
        )
        db.add(addr)
        db.commit()
        db.refresh(addr)
        return addr.id


# Apply override and client
app.dependency_overrides[get_db] = _setup_test_db()
client = TestClient(app)


def _register(email: str, password: str = "secret123"):
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    return r.json()


def _login(email: str, password: str = "secret123"):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()


def test_load_crud_happy_path():
    _register("load@example.com")
    tokens = _login("load@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # list empty
    res = client.get("/loads/", headers=headers)
    assert res.status_code == 200

    # prepare addresses
    pickup_id = _create_address()
    dropoff_id = _create_address(admin2="ATASEHIR")

    # create
    payload = {
        "name": "Gıda kolisi",
        "quantity_value": 250,
        "quantity_unit": "KG",
        "category": "GIDA",
        "pickup_address_id": pickup_id,
        "dropoff_address_id": dropoff_id,
        "pickup_day": "2025-12-31",
        "intl": False,
    }
    res = client.post("/loads/", json=payload, headers=headers)
    assert res.status_code == 201, res.text
    load_json = res.json()
    lid = load_json["id"]

    # get
    res = client.get(f"/loads/{lid}", headers=headers)
    assert res.status_code == 200

    # update
    res = client.patch(f"/loads/{lid}", json={"name": "Yeni Yük"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Yeni Yük"

    # delete
    res = client.delete(f"/loads/{lid}", headers=headers)
    assert res.status_code == 204

    # after delete
    res = client.get(f"/loads/{lid}", headers=headers)
    assert res.status_code == 404


def test_load_access_control():
    _register("l1@example.com")
    t1 = _login("l1@example.com")
    h1 = {"Authorization": f"Bearer {t1['access_token']}"}

    pickup_id = _create_address()
    dropoff_id = _create_address(admin2="ATASEHIR")

    res = client.post(
        "/loads/",
        json={
            "name": "Koli",
            "pickup_address_id": pickup_id,
            "dropoff_address_id": dropoff_id,
            "pickup_day": "2025-12-31",
            "intl": False,
        },
        headers=h1,
    )
    assert res.status_code == 201, res.text
    lid = res.json()["id"]

    _register("l2@example.com")
    t2 = _login("l2@example.com")
    h2 = {"Authorization": f"Bearer {t2['access_token']}"}

    res = client.get(f"/loads/{lid}", headers=h2)
    assert res.status_code == 404
    res = client.delete(f"/loads/{lid}", headers=h2)
    assert res.status_code == 403


def test_load_rbac_with_organization():
    _register("lowner@example.com")
    t_owner = _login("lowner@example.com")
    h_owner = {"Authorization": f"Bearer {t_owner['access_token']}"}

    # create org
    org = client.post("/orgs/", json={"title": "LoadOrg"}, headers=h_owner).json()
    org_id = org["id"]

    # prepare addresses
    pickup_id = _create_address()
    dropoff_id = _create_address(admin2="ATASEHIR")

    # another user cannot create under org
    _register("luser@example.com")
    t_user = _login("luser@example.com")
    h_user = {"Authorization": f"Bearer {t_user['access_token']}"}

    res = client.post(
        "/loads/",
        json={
            "organization_id": org_id,
            "name": "Koli",
            "pickup_address_id": pickup_id,
            "dropoff_address_id": dropoff_id,
            "pickup_day": "2025-12-31",
            "intl": False,
        },
        headers=h_user,
    )
    assert res.status_code == 403

    # make second user admin, then allowed
    u2_id = int(
        jwt.decode(
            t_user["access_token"],
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )["sub"]
    )  # type: ignore[index]
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        org_user_crud.assign_role(
            db, organization_id=org_id, user_id=u2_id, role=OrgRole.corporate_admin
        )
    finally:
        db.close()

    res = client.post(
        "/loads/",
        json={
            "organization_id": org_id,
            "name": "Koli",
            "pickup_address_id": pickup_id,
            "dropoff_address_id": dropoff_id,
            "pickup_day": "2025-12-31",
            "intl": False,
        },
        headers=h_user,
    )
    assert res.status_code == 201
    lid = res.json()["id"]

    # update/delete permitted
    res = client.patch(f"/loads/{lid}", json={"name": "Yeni"}, headers=h_user)
    assert res.status_code == 200
    res = client.delete(f"/loads/{lid}", headers=h_user)
    assert res.status_code == 204
