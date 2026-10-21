import logging
import time
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from common.errors import AppError

http_log = logging.getLogger("app.http")
error_log = logging.getLogger("app.errors")

_HTTP_CODES = {
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
}

# Pydantic error type -> stable code the frontend translates (see `validation.*` in the i18n files)
_VALIDATION_CODES = {
    "extra_forbidden": "UNKNOWN_FIELD",
    "greater_than": "TOO_SMALL",
    "greater_than_equal": "TOO_SMALL",
    "less_than": "TOO_LARGE",
    "less_than_equal": "TOO_LARGE",
    "literal_error": "INVALID_OPTION",
    "missing": "REQUIRED",
    "string_pattern_mismatch": "INVALID_FORMAT",
    "string_too_long": "TOO_LONG",
    "string_too_short": "TOO_SHORT",
    "too_long": "TOO_LONG",
    "too_short": "TOO_SHORT",
}
_TYPE_ERRORS = ("_type", "_parsing")  # e.g. string_type, int_parsing, float_type


def _validation_code(error_type: str) -> str:
    code = _VALIDATION_CODES.get(error_type)
    if code is None:
        code = "INVALID_TYPE" if error_type.endswith(_TYPE_ERRORS) else "INVALID_VALUE"
    return code


def _error(
    status: int,
    detail: str,
    code: str,
    *,
    params: dict[str, Any] | None = None,
    errors: list[dict] | None = None,
    headers=None,
):
    # `detail` is an English text for developers; the frontend translates `code`
    body: dict[str, Any] = {"code": code, "detail": detail}
    if params:
        body["params"] = params
    if errors:
        body["errors"] = errors
    return JSONResponse(status_code=status, content=body, headers=headers)


async def log_requests(request: Request, call_next):
    """Logs every request. It also catches unexpected errors: that way the 500 response goes
    through CORS and the frontend gets the error instead of a network failure."""
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        error_log.exception("Unhandled error on %s %s", request.method, request.url.path)
        response = _error(500, "Internal server error", "INTERNAL_ERROR")
    elapsed_ms = (time.perf_counter() - start) * 1000
    level = logging.WARNING if response.status_code >= 400 else logging.INFO
    http_log.log(
        level, "%s %s -> %s (%.0f ms)", request.method, request.url.path, response.status_code, elapsed_ms
    )
    return response


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return _error(exc.status_code, exc.message, exc.code, params=exc.params)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        errors = []
        for err in exc.errors():
            # loc = (source, field, ...): drop the source ("body", "query", "path")
            field = ".".join(str(part) for part in err["loc"][1:]) or str(err["loc"][0])
            item: dict[str, Any] = {
                "code": _validation_code(err["type"]),
                "field": field,
                "message": err["msg"],
            }
            # constraint values (min_length, ge, ...) so the frontend can interpolate them
            params = {
                name: value
                for name, value in (err.get("ctx") or {}).items()
                if isinstance(value, (str, int, float))
            }
            if params:
                item["params"] = params
            errors.append(item)
        return _error(422, "Invalid data", "VALIDATION_ERROR", errors=errors)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):
        code = _HTTP_CODES.get(exc.status_code, f"HTTP_{exc.status_code}")
        return _error(exc.status_code, str(exc.detail), code, headers=exc.headers)
