"""Account creation rules. There is no public registration by design."""

import pytest
from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.core.security import verify_password
from app.models import Teacher, UserRole
from app.services.user_service import UserService
from sqlalchemy.orm import Session

PASSWORD = "a-long-enough-password"


def test_creates_a_user_with_a_hashed_password(session: Session) -> None:
    user = UserService(session).create(
        email="head@example.org", password=PASSWORD, role=UserRole.HEAD_OF_STUDIES
    )

    assert user.id > 0
    assert user.hashed_password != PASSWORD
    assert verify_password(PASSWORD, user.hashed_password)


def test_rejects_a_duplicate_email(session: Session) -> None:
    service = UserService(session)
    service.create(email="head@example.org", password=PASSWORD, role=UserRole.ADMIN)

    with pytest.raises(ConflictError):
        service.create(email="head@example.org", password=PASSWORD, role=UserRole.ADMIN)


def test_rejects_a_short_password(session: Session) -> None:
    with pytest.raises(ValidationError):
        UserService(session).create(email="head@example.org", password="short", role=UserRole.ADMIN)


def test_rejects_an_unknown_teacher_link(session: Session) -> None:
    with pytest.raises(NotFoundError):
        UserService(session).create(
            email="teacher@example.org",
            password=PASSWORD,
            role=UserRole.TEACHER,
            teacher_id=999,
        )


def test_links_a_user_to_a_teacher(session: Session) -> None:
    teacher = Teacher(first_name="Ana", last_name="Garcia", email="ana.garcia@example.org")
    session.add(teacher)
    session.commit()

    user = UserService(session).create(
        email="ana.garcia@example.org",
        password=PASSWORD,
        role=UserRole.TEACHER,
        teacher_id=teacher.id,
    )

    assert user.teacher_id == teacher.id
