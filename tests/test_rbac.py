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
from app.models import org_user as _org_user  # noqa: F401
from app.models import organization as _organization  # noqa: F401
from app.models import user as _user  # noqa: F401
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


def test_org_update_delete_requires_admin():
    # owner creates org, becomes admin by default (in create endpoint)
    _register("owner@example.com")
    towner = _login("owner@example.com")
    h_owner = {"Authorization": f"Bearer {towner['access_token']}"}

    res = client.post("/orgs/", json={"title": "OrgRBAC"}, headers=h_owner)
    assert res.status_code == 201
    org_id = res.json()["id"]

    # another user tries to update/delete -> 403
    _register("user@example.com")
    tuser = _login("user@example.com")
    h_user = {"Authorization": f"Bearer {tuser['access_token']}"}

    res = client.patch(f"/orgs/{org_id}", json={"title": "X"}, headers=h_user)
    assert res.status_code == 403

    res = client.delete(f"/orgs/{org_id}", headers=h_user)
    assert res.status_code == 403

    # assign admin role to second user, then operations should pass
    # decode access token to get user id
    u2_id = int(
        jwt.decode(
            tuser["access_token"],
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )["sub"]
    )  # type: ignore[index]
    # use the same DB dependency to get a session
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        org_user_crud.assign_role(
            db, organization_id=org_id, user_id=u2_id, role=OrgRole.corporate_admin
        )
    finally:
        db.close()

    # now try update/delete again as second user
    res = client.patch(f"/orgs/{org_id}", json={"title": "Yeni"}, headers=h_user)
    assert res.status_code == 200
    res = client.delete(f"/orgs/{org_id}", headers=h_user)
    assert res.status_code == 204
