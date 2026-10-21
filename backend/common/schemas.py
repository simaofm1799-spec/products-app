from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int


class FieldError(BaseModel):
    field: str
    code: str  # e.g. REQUIRED, TOO_SHORT, INVALID_FORMAT
    message: str  # English, for developers
    params: dict[str, str | int | float] | None = None  # e.g. {"min_length": 1}


class ErrorResponse(BaseModel):
    detail: str  # English, for developers; the frontend translates `code`
    code: str  # e.g. INVALID_LOGIN, USER_NOT_FOUND, VALIDATION_ERROR
    params: dict[str, str | int | float] | None = None  # e.g. {"id": 99999}
    errors: list[FieldError] | None = None  # field errors, only on VALIDATION_ERROR


# Common error responses, used in the routers' `responses=` (shown in /docs).
ERROR_RESPONSES = {
    401: {"description": "Missing, invalid or expired token", "model": ErrorResponse},
    403: {"description": "The role of the user does not allow this action", "model": ErrorResponse},
    422: {"description": "Invalid data", "model": ErrorResponse},
    502: {"description": "Error contacting DummyJSON", "model": ErrorResponse},
    504: {"description": "DummyJSON timed out", "model": ErrorResponse},
}
NOT_FOUND_RESPONSE = {404: {"description": "Resource not found", "model": ErrorResponse}}


@dataclass
class ListParams:
    limit: int
    skip: int
    search: str | None
    sort_by: str | None
    order: Literal["asc", "desc"] | None


def list_params(
    limit: int = Query(30, ge=1, le=100, description="Items per page"),
    skip: int = Query(0, ge=0, description="Items to skip"),
    search: str | None = Query(None, alias="q", min_length=1, description="Text to search for"),
    sort_by: str | None = Query(None, alias="sortBy", description="Field to sort by"),
    order: Literal["asc", "desc"] | None = Query(None, description="Sort direction"),
) -> ListParams:
    return ListParams(limit=limit, skip=skip, search=search, sort_by=sort_by, order=order)
