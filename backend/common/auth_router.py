import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from common.dummyjson import dummyjson
from common.errors import AppError, BadRequestError, UnauthorizedError
from common.schemas import ERROR_RESPONSES
from common.security import create_token, get_current_user

log = logging.getLogger("app.auth")

router = APIRouter(prefix="/api", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", summary="Log in and get a JWT", responses={401: ERROR_RESPONSES[401], 502: ERROR_RESPONSES[502]})
async def login(data: LoginRequest):
    try:
        user = await dummyjson.request(
            "POST", "/auth/login", json={"password": data.password, "username": data.username}
        )
    except BadRequestError:
        log.info("Failed login for '%s'", data.username)
        raise UnauthorizedError("Invalid username or password", code="INVALID_LOGIN")

    # DummyJSON's login does not return the role; it comes from the full profile.
    try:
        profile = await dummyjson.request("GET", f"/users/{user['id']}")
        user["role"] = profile.get("role", "user")
    except AppError:
        log.warning("Could not fetch the role of '%s'; assuming 'user'", data.username)

    log.info("Successful login: '%s'", data.username)
    return {"access_token": create_token(user), "token_type": "bearer"}


@router.get("/me", summary="Get the authenticated user", responses={401: ERROR_RESPONSES[401]})
def me(payload: dict = Depends(get_current_user)):
    return {
        "id": payload["sub"],
        "email": payload.get("email"),
        "firstName": payload.get("firstName"),
        "image": payload.get("image"),  # absent in tokens issued before this field existed
        "lastName": payload.get("lastName"),
        "role": payload["role"],
        "username": payload["username"],
    }
