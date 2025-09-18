from fastapi.testclient import TestClient

from app.deps import get_db, get_settings
from app.main import app
from app.security import create_access_token


def test_get_settings_returns_settings():
    s = get_settings()
    assert hasattr(s, "ENV") and hasattr(s, "DATABASE_URL")


def test_get_db_generator_closes():
    gen = get_db()
    db = next(gen)
    assert db is not None
    # trigger finally: db.close()
    gen.close()


def test_me_nonexistent_user_unauthorized():
    token = create_access_token("999999")  # ID var olmayan kullanıcı
    headers = {"Authorization": f"Bearer {token}"}
    client = TestClient(app)
    res = client.get("/auth/me", headers=headers)
    assert res.status_code == 401
