from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from common.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET
from common.errors import ForbiddenError, UnauthorizedError

# auto_error=False: we raise the 401 ourselves, in the API's error format
bearer_scheme = HTTPBearer(auto_error=False)


def create_token(user: dict) -> str:
    payload = {
        "sub": str(user["id"]),  # the user id comes first, the rest is alphabetical
        "email": user.get("email"),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES),
        "firstName": user.get("firstName"),
        "image": user.get("image"),
        "lastName": user.get("lastName"),
        "role": user.get("role", "user"),
        "username": user["username"],
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise UnauthorizedError("Missing token", code="TOKEN_MISSING")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired", code="TOKEN_EXPIRED")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token", code="TOKEN_INVALID")
    return payload


def require_role(*allowed_roles: str):
    """Dependency that only lets through users whose role (read from the signed JWT, never from
    the request) is one of `allowed_roles`. Anything else, an unknown role included, gets a 403."""

    def check_role(payload: dict = Depends(get_current_user)) -> dict:
        if payload.get("role") not in allowed_roles:
            raise ForbiddenError(params={"role": str(payload.get("role"))})
        return payload

    return check_role


# Permission matrix (see docs/PERMISSIONS.md): everybody reads; moderators also update;
# only admins create and delete.
require_creator = require_role("admin")
require_deleter = require_role("admin")
require_editor = require_role("admin", "moderator")
