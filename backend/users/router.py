from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, Response, status

from common.schemas import ERROR_RESPONSES, NOT_FOUND_RESPONSE, Page
from common.security import get_current_user, require_creator, require_deleter, require_editor
from users.query import UserListQuery
from users.schemas import Distribution, UserCreate, UserResponse, UserUpdate
from users.service import user_service

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)],
    responses=ERROR_RESPONSES,
)

UserId = Path(ge=1, description="User id")


@router.get("", response_model=Page[UserResponse], summary="List users")
async def list_users(query: Annotated[UserListQuery, Query()]):
    return await user_service.list(query)


# declared before "/{user_id}" so that "distribution" is not read as a user id
@router.get("/distribution", response_model=Distribution, summary="Users per state or university")
async def users_distribution(by: Literal["state", "university"] = Query(description="Field to count by")):
    return await user_service.distribution(by)


@router.get("/{user_id}", response_model=UserResponse, responses=NOT_FOUND_RESPONSE, summary="Get user")
async def get_user(user_id: int = UserId):
    return await user_service.get(user_id)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_creator)],
    summary="Create user",
)
async def create_user(body: UserCreate):
    return await user_service.create(body.model_dump(exclude_unset=True))


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_editor)],
    responses=NOT_FOUND_RESPONSE,
    summary="Update user",
)
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_editor)],
    responses=NOT_FOUND_RESPONSE,
    include_in_schema=False,
)
async def update_user(body: UserUpdate, user_id: int = UserId):
    return await user_service.update(user_id, body.model_dump(exclude_unset=True))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_deleter)],
    responses=NOT_FOUND_RESPONSE,
    summary="Delete user",
)
async def delete_user(user_id: int = UserId):
    await user_service.delete(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
