"""Business rules for user accounts.

There is deliberately no public registration: a school's staff list is not
self-service. Accounts are created by an administrator, and the very first one is
created from the command line (``scripts/create_user.py``).
"""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.school import Teacher
from app.models.user import User
from app.repositories.user_repository import UserRepository

MINIMUM_PASSWORD_LENGTH = 12


class UserService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def list_all(self) -> Sequence[User]:
        return self.users.list_all()

    def count(self) -> int:
        return len(self.users.list_all())

    def create(
        self,
        email: str,
        password: str,
        role: UserRole,
        teacher_id: int | None = None,
    ) -> User:
        if self.users.get_by_email(email) is not None:
            raise ConflictError(f"A user with email {email} already exists")
        if len(password) < MINIMUM_PASSWORD_LENGTH:
            raise ValidationError(
                f"The password must be at least {MINIMUM_PASSWORD_LENGTH} characters long"
            )
        if teacher_id is not None and self.session.get(Teacher, teacher_id) is None:
            raise NotFoundError(f"Teacher {teacher_id} not found")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role=role,
            teacher_id=teacher_id,
        )
        self.users.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
