from contextlib import contextmanager
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.deps import get_db
from app.models.base import Base
# Import all models so SQLAlchemy mappers are registered before create_all
from app.models import user as _user  # noqa: F401
from app.models import organization as _organization  # noqa: F401
from app.models import org_user as _org_user  # noqa: F401
from app.models import address as _address  # noqa: F401
from app.models import vehicle as _vehicle  # noqa: F401
from app.models import load as _load  # noqa: F401
from app.models import offer as _offer  # noqa: F401
from app.models import match as _match  # noqa: F401
from app.models import rating as _rating  # noqa: F401
from app.models import membership as _membership  # noqa: F401


def _setup_test_db():
    # In-memory SQLite for fast, isolated tests
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


# Apply dependency override at module import time
app.dependency_overrides[get_db] = _setup_test_db()
client = TestClient(app)


def test_register_success():
    payload = {
        "email": "test@example.com",
        "password": "secret123",
        "phone": "+905551112233",
        "locale": "tr",
    }
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["email"] == payload["email"]
    assert "id" in data


def test_register_duplicate_email():
    payload = {
        "email": "dup@example.com",
        "password": "secret123",
    }
    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code == 400
    assert "zaten" in r2.json().get("detail", "").lower()


def test_login_success():
    email = "login@example.com"
    password = "secret123"
    # Register first
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    # Login
    res = client.post("/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data and data["access_token"]
    assert "refresh_token" in data and data["refresh_token"]
    assert data.get("token_type") == "bearer"


def test_login_invalid_credentials():
    email = "bad@example.com"
    password = "secret123"
    client.post("/auth/register", json={"email": email, "password": password})
    res = client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert res.status_code == 401
    assert "geçersiz" in res.json().get("detail", "").lower()
