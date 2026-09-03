"""Shared fixtures. Every test gets an isolated in-memory database."""

from collections.abc import Iterator

import pytest
from app.api.deps import get_current_user
from app.core.db import get_session
from app.main import create_app
from app.models import Base, User, UserRole
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, future=True)
    with factory() as db_session:
        yield db_session
    Base.metadata.drop_all(engine)


@pytest.fixture
def admin_user(session: Session) -> User:
    user = User(email="admin@example.org", hashed_password="x", role=UserRole.ADMIN)
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def client(session: Session, admin_user: User) -> Iterator[TestClient]:
    """An API client authenticated as an admin.

    Authentication itself is tested in ``test_auth.py``; every other test
    overrides it so it can focus on its own behaviour.
    """
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: admin_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
