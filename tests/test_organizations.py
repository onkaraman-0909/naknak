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
from app.models import org_user as _org_user  # noqa: F401
from app.models import organization as _organization  # noqa: F401
from app.models import user as _user  # noqa: F401
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


def test_org_crud_happy_path():
    _register("own@example.com")
    tokens = _login("own@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # list empty
    res = client.get("/orgs/", headers=headers)
    assert res.status_code == 200

    # create
    payload = {"title": "F4ST Lojistik", "tax_office": "Kadıköy", "tax_number": "123"}
    res = client.post("/orgs/", json=payload, headers=headers)
    assert res.status_code == 201
    org = res.json()
    assert org["title"] == payload["title"]
    org_id = org["id"]

    # get
    res = client.get(f"/orgs/{org_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == org_id

    # update
    res = client.patch(f"/orgs/{org_id}", json={"title": "Yeni Ünvan"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Yeni Ünvan"

    # delete
    res = client.delete(f"/orgs/{org_id}", headers=headers)
    assert res.status_code == 204

    # get after delete -> 404
    res = client.get(f"/orgs/{org_id}", headers=headers)
    assert res.status_code == 404


def test_org_access_control():
    # owner1 creates org
    _register("a@example.com")
    t1 = _login("a@example.com")
    h1 = {"Authorization": f"Bearer {t1['access_token']}"}
    res = client.post("/orgs/", json={"title": "OrgA"}, headers=h1)
    assert res.status_code == 201
    org_id = res.json()["id"]

    # another user cannot see/delete
    _register("b@example.com")
    t2 = _login("b@example.com")
    h2 = {"Authorization": f"Bearer {t2['access_token']}"}

    res = client.get(f"/orgs/{org_id}", headers=h2)
    assert res.status_code == 404
    res = client.delete(f"/orgs/{org_id}", headers=h2)
    assert res.status_code == 403
