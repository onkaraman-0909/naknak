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
from app.models import organization as _organization  # noqa: F401
from app.models import user as _user  # noqa: F401
from app.models import vehicle as _vehicle  # noqa: F401
from app.models.base import Base
from app.models.enums import OrgRole


def _setup_test_db():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    @contextmanager
    def _session_scope() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
            db.commit()
        finally:
            db.close()

    def override_get_db() -> Generator[Session, None, None]:
        with _session_scope() as s:
            yield s

    return override_get_db


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


def test_vehicle_crud_happy_path():
    _register("veh@example.com")
    tokens = _login("veh@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # list empty
    res = client.get("/vehicles/", headers=headers)
    assert res.status_code == 200

    # create
    payload = {"capacity_value": 1000, "capacity_unit": "KG", "can_food": True}
    res = client.post("/vehicles/", json=payload, headers=headers)
    assert res.status_code == 201, res.text
    v = res.json()
    vid = v["id"]

    # get
    res = client.get(f"/vehicles/{vid}", headers=headers)
    assert res.status_code == 200

    # update
    res = client.patch(f"/vehicles/{vid}", json={"can_dg": True}, headers=headers)
    assert res.status_code == 200
    assert res.json()["can_dg"] is True

    # delete
    res = client.delete(f"/vehicles/{vid}", headers=headers)
    assert res.status_code == 204

    # get after delete
    res = client.get(f"/vehicles/{vid}", headers=headers)
    assert res.status_code == 404


def test_vehicle_access_control():
    _register("v1@example.com")
    t1 = _login("v1@example.com")
    h1 = {"Authorization": f"Bearer {t1['access_token']}"}

    res = client.post("/vehicles/", json={"capacity_value": 500}, headers=h1)
    assert res.status_code == 201
    vid = res.json()["id"]

    _register("v2@example.com")
    t2 = _login("v2@example.com")
    h2 = {"Authorization": f"Bearer {t2['access_token']}"}

    res = client.get(f"/vehicles/{vid}", headers=h2)
    assert res.status_code == 404
    res = client.delete(f"/vehicles/{vid}", headers=h2)
    assert res.status_code == 403


def test_vehicle_rbac_with_organization():
    # owner creates org
    _register("own2@example.com")
    t_owner = _login("own2@example.com")
    h_owner = {"Authorization": f"Bearer {t_owner['access_token']}"}

    org = client.post("/orgs/", json={"title": "VehOrg"}, headers=h_owner).json()
    org_id = org["id"]

    # another user cannot create vehicle under org unless admin
    _register("vv@example.com")
    t_user = _login("vv@example.com")
    h_user = {"Authorization": f"Bearer {t_user['access_token']}"}

    res = client.post(
        "/vehicles/",
        json={"organization_id": org_id, "capacity_value": 1},
        headers=h_user,
    )
    assert res.status_code == 403

    # make second user admin for the org
    u2_id = int(
        jwt.decode(
            t_user["access_token"],
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )["sub"]
    )  # type: ignore[index]
    # get DB session from app deps
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        org_user_crud.assign_role(
            db, organization_id=org_id, user_id=u2_id, role=OrgRole.corporate_admin
        )
    finally:
        db.close()

    # now can create under org
    res = client.post(
        "/vehicles/",
        json={"organization_id": org_id, "capacity_value": 1},
        headers=h_user,
    )
    assert res.status_code == 201
    vid = res.json()["id"]

    # update/delete also permitted as admin
    res = client.patch(f"/vehicles/{vid}", json={"can_dg": True}, headers=h_user)
    assert res.status_code == 200
    res = client.delete(f"/vehicles/{vid}", headers=h_user)
    assert res.status_code == 204
