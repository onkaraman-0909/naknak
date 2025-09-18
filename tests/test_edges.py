import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security import (
    create_access_token,
    create_refresh_token,
    get_subject_from_token,
)

client = TestClient(app)


def test_get_subject_from_token_type_mismatch():
    sub = "42"
    refresh = create_refresh_token(sub)
    with pytest.raises(ValueError):
        get_subject_from_token(refresh, expected_type="access")


def test_get_subject_from_token_invalid_sub(monkeypatch):
    # forge a token with empty subject
    access = create_access_token("")
    with pytest.raises(ValueError):
        get_subject_from_token(access, expected_type="access")


def test_me_without_token_unauthorized():
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_me_with_refresh_token_unauthorized():
    # login flow to get refresh token
    email = "edge@example.com"
    password = "secret123"
    client.post("/auth/register", json={"email": email, "password": password})
    login = client.post("/auth/login", json={"email": email, "password": password})
    tokens = login.json()

    headers = {"Authorization": f"Bearer {tokens['refresh_token']}"}
    res = client.get("/auth/me", headers=headers)
    assert res.status_code == 401
