from contextlib import contextmanager
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.deps import get_db
from app.main import app

# ensure models registered
from app.models import address as _address  # noqa: F401
from app.models import load as _load  # noqa: F401
from app.models import organization as _organization  # noqa: F401
from app.models import user as _user  # noqa: F401
from app.models import vehicle as _vehicle  # noqa: F401
from app.models.base import Base


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


def _create_address(db: Session) -> int:
    from app.models.address import Address

    a = Address(
        country="TR", admin1="IST", admin2="KADIKOY", admin3=None, line_optional=None
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a.id


def test_orgs_pagination_limit():
    _register("pg@example.com")
    tokens = _login("pg@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # create 2 orgs
    r1 = client.post("/orgs/", json={"title": "AA"}, headers=headers)
    r2 = client.post("/orgs/", json={"title": "BB"}, headers=headers)
    assert r1.status_code == 201, r1.text
    assert r2.status_code == 201, r2.text

    res = client.get("/orgs/?limit=1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list) and len(data) == 1


def test_vehicles_pagination_and_filter():
    _register("pv@example.com")
    tokens = _login("pv@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # create org
    org = client.post("/orgs/", json={"title": "VOrg"}, headers=headers).json()
    org_id = org["id"]

    # create 2 vehicles: one under org, one personal
    client.post(
        "/vehicles/",
        json={"organization_id": org_id, "capacity_value": 1},
        headers=headers,
    )
    client.post("/vehicles/", json={"capacity_value": 2}, headers=headers)

    # filter by organization_id should return 1
    res = client.get(f"/vehicles/?organization_id={org_id}", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # limit should restrict count
    res = client.get("/vehicles/?limit=1", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_loads_pagination_and_filter():
    _register("pl@example.com")
    tokens = _login("pl@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # create org
    org = client.post("/orgs/", json={"title": "LOrg"}, headers=headers).json()
    org_id = org["id"]

    # create addresses
    # obtain a session from deps
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        pick = _create_address(db)
        drop = _create_address(db)
    finally:
        db.close()

    # create 2 loads, one with org and one personal
    client.post(
        "/loads/",
        json={
            "organization_id": org_id,
            "name": "Koli1",
            "pickup_address_id": pick,
            "dropoff_address_id": drop,
            "pickup_day": "2025-12-31",
            "intl": False,
        },
        headers=headers,
    )
    client.post(
        "/loads/",
        json={
            "name": "Koli2",
            "pickup_address_id": pick,
            "dropoff_address_id": drop,
            "pickup_day": "2025-12-31",
            "intl": False,
        },
        headers=headers,
    )

    res = client.get(f"/loads/?organization_id={org_id}", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1

    res = client.get("/loads/?limit=1", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
