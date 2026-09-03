"""Authentication behaviour, exercised without the auth override."""

from app.core.db import get_session
from app.core.security import hash_password
from app.main import create_app
from app.models import User, UserRole
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _client_with(session: Session) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)


def test_logs_in_and_reads_the_current_user(session: Session) -> None:
    session.add(
        User(
            email="head@example.org",
            hashed_password=hash_password("secret123"),
            role=UserRole.HEAD_OF_STUDIES,
        )
    )
    session.commit()
    client = _client_with(session)

    response = client.post(
        "/api/v1/auth/login", json={"email": "head@example.org", "password": "secret123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["role"] == "head_of_studies"


def test_rejects_a_wrong_password(session: Session) -> None:
    session.add(
        User(
            email="head@example.org",
            hashed_password=hash_password("secret123"),
            role=UserRole.ADMIN,
        )
    )
    session.commit()

    response = _client_with(session).post(
        "/api/v1/auth/login", json={"email": "head@example.org", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["code"] == "authentication_error"


def test_requires_a_token(session: Session) -> None:
    assert _client_with(session).get("/api/v1/teachers").status_code == 401
