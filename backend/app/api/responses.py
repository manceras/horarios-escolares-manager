"""Error responses declared on every router.

They exist so the generated OpenAPI document -- and therefore the frontend
client -- knows the shape of a failure, not only of a success.
"""

from typing import Any

from app.schemas.common import ErrorResponse

ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "The resource does not exist"},
    409: {"model": ErrorResponse, "description": "The request conflicts with the current state"},
    422: {"model": ErrorResponse, "description": "The request breaks a business rule"},
}
