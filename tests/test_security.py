from jose import jwt

from app.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.config import settings


def test_password_hash_and_verify():
    raw = "secret123"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)
    assert not verify_password("wrong", hashed)


def test_create_access_and_refresh_tokens():
    sub = "123"
    access = create_access_token(sub)
    refresh = create_refresh_token(sub)

    # Decode and assert token structure
    decoded_access = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    decoded_refresh = jwt.decode(refresh, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    assert decoded_access["sub"] == sub
    assert decoded_access["type"] == "access"
    assert "exp" in decoded_access and isinstance(decoded_access["exp"], int)

    assert decoded_refresh["sub"] == sub
    assert decoded_refresh["type"] == "refresh"
    assert "exp" in decoded_refresh and isinstance(decoded_refresh["exp"], int)
