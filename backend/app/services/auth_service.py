"""Authentication: verifying credentials and issuing access tokens."""

from sqlalchemy.orm import Session

from app.core.errors import AuthenticationError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: Session) -> None:
        self.users = UserRepository(session)

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        # Same message for unknown user and wrong password: do not leak which one it was.
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        if not user.active:
            raise AuthenticationError("This account is disabled")
        return user

    def issue_token(self, user: User) -> str:
        return create_access_token(subject=str(user.id), role=user.role)
