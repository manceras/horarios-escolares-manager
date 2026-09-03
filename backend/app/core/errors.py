"""Domain errors.

Services raise these; the API layer translates them into HTTP responses. Nothing
outside ``app/api`` may raise ``HTTPException``.
"""


class DomainError(Exception):
    """Base class for every expected, business-level failure."""

    code = "domain_error"
    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    code = "not_found"
    status_code = 404


class ConflictError(DomainError):
    """The request contradicts the current state (duplicate, overlap, ...)."""

    code = "conflict"
    status_code = 409


class ValidationError(DomainError):
    """The request is well-formed but breaks a business rule."""

    code = "validation_error"
    status_code = 422


class PermissionDeniedError(DomainError):
    code = "permission_denied"
    status_code = 403


class AuthenticationError(DomainError):
    code = "authentication_error"
    status_code = 401
