from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import pytest

from app.models.base import Base
from app.crud import user as user_crud
# ensure models are registered
from app.models import user as _user  # noqa: F401


@contextmanager
def setup_db() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def test_create_and_get_user():
    with setup_db() as db:
        u = user_crud.create(db, email="ucase@example.com", password="secret123")
        assert u.id is not None
        fetched = user_crud.get_by_email(db, "ucase@example.com")
        assert fetched is not None
        assert fetched.id == u.id
        assert fetched.email == "ucase@example.com"


def test_unique_email_constraint():
    with setup_db() as db:
        user_crud.create(db, email="dup2@example.com", password="secret123")
        with pytest.raises(Exception):
            user_crud.create(db, email="dup2@example.com", password="secret123")
        # Ensure session is usable after expected failure
        db.rollback()
