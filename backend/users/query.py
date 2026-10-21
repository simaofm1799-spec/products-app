from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from users.schemas import Gender, Role

# Fields the list can be sorted by (the same keys the frontend table uses for its columns)
SortField = Literal[
    "address.city",
    "address.country",
    "address.state",
    "age",
    "birthDate",
    "bloodGroup",
    "company.name",
    "email",
    "eyeColor",
    "firstName",
    "gender",
    "height",
    "id",
    "phone",
    "role",
    "username",
    "weight",
]

# query parameter -> path of the field it filters
_TEXT_FILTERS = {
    "birthDate": "birthDate",
    "city": "address.city",
    "company": "company.name",
    "country": "address.country",
    "email": "email",
    "phone": "phone",
    "state": "address.state",
    "username": "username",
}
_EXACT_FILTERS = {
    "bloodGroup": "bloodGroup",
    "eyeColor": "eyeColor",
    "gender": "gender",
    "role": "role",
}
_RANGE_FILTERS = {
    "age": "age",
    "height": "height",
    "weight": "weight",
}


class UserListQuery(BaseModel):
    """Query of `GET /api/users`: pagination, sorting and one optional filter per table column.
    When several filters are given, a user has to match all of them."""

    model_config = ConfigDict(extra="forbid")

    limit: int = Field(30, ge=1, le=100, description="Items per page")
    skip: int = Field(0, ge=0, description="Items to skip")
    order: Literal["asc", "desc"] = Field("asc", description="Sort direction")
    sortBy: SortField | None = Field(None, description="Field to sort by")

    # contains the text (case-insensitive)
    birthDate: str | None = Field(None, min_length=1, max_length=50)
    city: str | None = Field(None, min_length=1, max_length=100)
    company: str | None = Field(None, min_length=1, max_length=100)
    country: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, min_length=1, max_length=254)
    name: str | None = Field(None, min_length=1, max_length=100, description="First or last name")
    phone: str | None = Field(None, min_length=1, max_length=30)
    state: str | None = Field(None, min_length=1, max_length=100)
    username: str | None = Field(None, min_length=1, max_length=50)

    # equals the value (case-insensitive)
    bloodGroup: str | None = Field(None, min_length=1, max_length=5)
    eyeColor: str | None = Field(None, min_length=1, max_length=30)
    gender: Gender | None = None
    role: Role | None = None

    # numbers
    id: int | None = Field(None, ge=1)
    ageMax: int | None = None
    ageMin: int | None = None
    heightMax: float | None = None
    heightMin: float | None = None
    weightMax: float | None = None
    weightMin: float | None = None


def value_at(user: dict[str, Any], path: str) -> Any:
    value: Any = user
    for part in path.split("."):
        value = value.get(part) if isinstance(value, dict) else None
    return value


def _date_parts(value: Any) -> tuple[int, ...]:
    """'1996-5-30' -> (1996, 5, 30): dates come without zeros, so as text they would sort wrongly
    ('1996-10-2' before '1996-5-30')."""
    parts = str(value).split("-")
    return tuple(int(part) for part in parts) if all(part.isdigit() for part in parts) else (0,)


def _matches(user: dict[str, Any], query: UserListQuery) -> bool:
    checks: list[bool] = []
    if query.name is not None:
        full_name = f"{user.get('firstName') or ''} {user.get('lastName') or ''}"
        checks.append(query.name.lower() in full_name.lower())
    for param, path in _TEXT_FILTERS.items():
        wanted = getattr(query, param)
        if wanted is not None:
            if param == "birthDate":
                wanted = wanted.replace("/", "-")  # the frontend shows dates as YYYY/M/D
            checks.append(wanted.lower() in str(value_at(user, path) or "").lower())
    for param, path in _EXACT_FILTERS.items():
        wanted = getattr(query, param)
        if wanted is not None:
            checks.append(str(value_at(user, path) or "").lower() == wanted.lower())
    if query.id is not None:
        checks.append(user.get("id") == query.id)
    for param, path in _RANGE_FILTERS.items():
        value = value_at(user, path)
        minimum = getattr(query, f"{param}Min")
        maximum = getattr(query, f"{param}Max")
        if minimum is not None:
            checks.append(value is not None and value >= minimum)
        if maximum is not None:
            checks.append(value is not None and value <= maximum)
    return all(checks)


def filter_users(users: list[dict[str, Any]], query: UserListQuery) -> list[dict[str, Any]]:
    return [user for user in users if _matches(user, query)]


def sort_users(
    users: list[dict[str, Any]], sort_by: str | None, order: str
) -> list[dict[str, Any]]:
    """Users without a value for the field always go last, whatever the direction."""
    result = users
    if sort_by is not None:

        def sort_key(user: dict[str, Any]) -> tuple:
            value = value_at(user, sort_by)
            if sort_by == "birthDate":
                normalized = _date_parts(value)
            else:
                normalized = value.lower() if isinstance(value, str) else value
            return (normalized, str(user.get("lastName") or "").lower())

        with_value = [user for user in users if value_at(user, sort_by) is not None]
        without_value = [user for user in users if value_at(user, sort_by) is None]
        result = sorted(with_value, key=sort_key, reverse=order == "desc") + without_value
    return result
