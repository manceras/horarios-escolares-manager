"""Login and current-user endpoints."""

from fastapi import APIRouter

from app.api.deps import AuthServiceDep, CurrentUser
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, service: AuthServiceDep) -> TokenResponse:
    user = service.authenticate(payload.email, payload.password)
    return TokenResponse(access_token=service.issue_token(user))


@router.get("/me", response_model=UserRead)
def read_current_user(user: CurrentUser) -> User:
    return user
