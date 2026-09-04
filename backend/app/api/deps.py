"""Shared FastAPI dependencies: session, services, authentication and roles."""

from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.core.security import decode_access_token
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.curriculum_service import CurriculumEntryService
from app.services.teacher_service import TeacherService

SessionDep = Annotated[Session, Depends(get_session)]

_bearer = HTTPBearer(auto_error=True)
CredentialsDep = Annotated[HTTPAuthorizationCredentials, Depends(_bearer)]


def get_current_user(credentials: CredentialsDep, session: SessionDep) -> User:
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise invalid from exc

    subject = payload.get("sub")
    if subject is None:
        raise invalid

    user = UserRepository(session).get(int(subject))
    if user is None or not user.active:
        raise invalid
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    """Dependency factory restricting an endpoint to the given roles."""

    def dependency(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this resource",
            )
        return user

    return dependency


# Common role bundles. Use these instead of repeating role lists in routers.
StaffUser = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.HEAD_OF_STUDIES))]
AnyUser = Annotated[
    User, Depends(require_roles(UserRole.ADMIN, UserRole.HEAD_OF_STUDIES, UserRole.TEACHER))
]


def get_teacher_service(session: SessionDep) -> TeacherService:
    return TeacherService(session)


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


def get_curriculum_service(session: SessionDep) -> CurriculumEntryService:
    return CurriculumEntryService(session)


TeacherServiceDep = Annotated[TeacherService, Depends(get_teacher_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurriculumServiceDep = Annotated[CurriculumEntryService, Depends(get_curriculum_service)]
