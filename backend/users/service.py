import logging
from collections import Counter
from typing import Any

from common.dummyjson import dummyjson
from common.errors import NotFoundError
from users.query import UserListQuery, filter_users, sort_users, value_at
from users.schemas import UserResponse

log = logging.getLogger("app.users")

# Only these fields are requested to DummyJSON (never password, ssn, bank data, ...)
USER_FIELDS = ",".join(name for name in UserResponse.model_fields if name != "id")
# `by` of the distribution -> path of the user field that is counted
DISTRIBUTION_FIELDS = {"state": "address.state", "university": "university"}


class UserService:
    """Calls to the DummyJSON users API (https://dummyjson.com/docs/users)."""

    async def _all_users(self) -> list[dict[str, Any]]:
        # GET /users?limit=0&select=...  (limit=0 returns every user)
        data = await dummyjson.request(
            "GET", "/users", params={"limit": 0, "select": USER_FIELDS}
        )
        log.info("Users loaded from DummyJSON (%s)", len(data["users"]))
        return data["users"]

    async def list(self, query: UserListQuery) -> dict[str, Any]:
        users = await self._all_users()
        matching = sort_users(filter_users(users, query), query.sortBy, query.order)
        return {
            "items": matching[query.skip : query.skip + query.limit],
            "limit": query.limit,
            "skip": query.skip,
            "total": len(matching),
        }

    async def distribution(self, by: str) -> dict[str, Any]:
        users = await self._all_users()
        counts = Counter(
            value for user in users if (value := value_at(user, DISTRIBUTION_FIELDS[by]))
        )
        # most users first; same count -> alphabetical
        ranked = sorted(counts.items(), key=lambda entry: (-entry[1], entry[0].lower()))
        return {
            "by": by,
            "items": [{"count": count, "label": label} for label, count in ranked],
            "total": sum(counts.values()),
        }

    async def get(self, user_id: int) -> dict[str, Any]:
        # GET /users/{id}
        return await dummyjson.request(
            "GET", f"/users/{user_id}", not_found=self._not_found(user_id)
        )

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        # POST /users/add
        created = await dummyjson.request("POST", "/users/add", json=data)
        log.info("User created (id=%s)", created.get("id"))
        return created

    async def update(self, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        # PUT /users/{id}
        updated = await dummyjson.request(
            "PUT", f"/users/{user_id}", json=data, not_found=self._not_found(user_id)
        )
        log.info("User updated (id=%s, fields=%s)", user_id, sorted(data))
        return updated

    async def delete(self, user_id: int) -> None:
        # DELETE /users/{id}
        await dummyjson.request(
            "DELETE", f"/users/{user_id}", not_found=self._not_found(user_id)
        )
        log.info("User deleted (id=%s)", user_id)

    @staticmethod
    def _not_found(user_id: int) -> NotFoundError:
        return NotFoundError(
            f"User {user_id} not found", code="USER_NOT_FOUND", params={"id": user_id}
        )


user_service = UserService()
