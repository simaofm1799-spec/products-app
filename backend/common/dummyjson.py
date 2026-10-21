import logging
from typing import Any

import httpx

from common.config import DUMMYJSON_TIMEOUT, DUMMYJSON_URL
from common.errors import (
    BadRequestError,
    NotFoundError,
    UpstreamError,
    UpstreamTimeoutError,
)
from common.schemas import ListParams

log = logging.getLogger("app.dummyjson")


def _upstream_message(resp: httpx.Response) -> str:
    try:
        message = resp.json().get("message") or resp.text
    except ValueError:
        message = resp.text
    return message


def _raise_for_status(
    method: str, path: str, resp: httpx.Response, not_found: NotFoundError | None
) -> None:
    """Translates an unsuccessful DummyJSON response into an application error (always raises)."""
    message = _upstream_message(resp)
    if resp.status_code == 404:
        raise not_found or NotFoundError(message)
    if resp.status_code == 400:
        raise BadRequestError(message)
    log.error("Unexpected response: %s %s -> %s %s", method, path, resp.status_code, message)
    raise UpstreamError()


class DummyJsonClient:
    """Shared HTTP client; translates DummyJSON failures into application errors."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient(base_url=DUMMYJSON_URL, timeout=DUMMYJSON_TIMEOUT)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        not_found: NotFoundError | None = None,
    ) -> Any:
        """`not_found` is the error raised if DummyJSON answers 404 (lets each domain set its own code)."""
        params = {name: value for name, value in (params or {}).items() if value is not None}
        try:
            resp = await self._client.request(method, path, params=params, json=json)
        except httpx.TimeoutException:
            log.error("Timeout: %s %s", method, path)
            raise UpstreamTimeoutError()
        except httpx.HTTPError as exc:
            log.error("Unavailable: %s %s (%s)", method, path, type(exc).__name__)
            raise UpstreamError()

        log.debug("%s %s -> %s", method, path, resp.status_code)
        if not resp.is_success:
            _raise_for_status(method, path, resp, not_found)
        return resp.json()


dummyjson = DummyJsonClient()


class DummyJsonResource:
    """Generic CRUD over a DummyJSON resource. Each domain subclasses it and sets the attributes."""

    path: str  # e.g. "/products"
    list_key: str  # key of the list in the response, e.g. "products"
    label: str  # readable name used in logs and messages, e.g. "Product"
    not_found_code: str  # e.g. "PRODUCT_NOT_FOUND"

    async def list(self, params: ListParams) -> dict[str, Any]:
        path = f"{self.path}/search" if params.search else self.path
        data = await dummyjson.request(
            "GET",
            path,
            params={
                "limit": params.limit,
                "order": params.order,
                "q": params.search,
                "skip": params.skip,
                "sortBy": params.sort_by,
            },
        )
        return {
            "items": data[self.list_key],
            "limit": data["limit"],
            "skip": data["skip"],
            "total": data["total"],
        }

    async def get(self, item_id: int) -> dict[str, Any]:
        return await dummyjson.request(
            "GET", f"{self.path}/{item_id}", not_found=self._not_found(item_id)
        )

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        created = await dummyjson.request("POST", f"{self.path}/add", json=data)
        self._log.info("%s created (id=%s)", self.label, created.get("id"))
        return created

    async def update(self, item_id: int, data: dict[str, Any]) -> dict[str, Any]:
        updated = await dummyjson.request(
            "PUT", f"{self.path}/{item_id}", json=data, not_found=self._not_found(item_id)
        )
        self._log.info("%s updated (id=%s, fields=%s)", self.label, item_id, sorted(data))
        return updated

    async def delete(self, item_id: int) -> None:
        await dummyjson.request(
            "DELETE", f"{self.path}/{item_id}", not_found=self._not_found(item_id)
        )
        self._log.info("%s deleted (id=%s)", self.label, item_id)

    @property
    def _log(self) -> logging.Logger:
        return logging.getLogger(f"app.{self.list_key}")

    def _not_found(self, item_id: int) -> NotFoundError:
        return NotFoundError(
            f"{self.label} {item_id} not found", code=self.not_found_code, params={"id": item_id}
        )
