from typing import Any


class AppError(Exception):
    """Application error mapped to an HTTP response.

    `message` is an English text for developers/logs. The frontend must not show it:
    it translates `code` (plus `params`, for interpolation) using its own i18n labels.
    """

    status_code = 500
    code = "INTERNAL_ERROR"
    default_message = "Internal server error"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        params: dict[str, Any] | None = None,
    ):
        self.message = message or self.default_message
        self.code = code or self.code
        self.params = params
        super().__init__(self.message)


class BadRequestError(AppError):
    status_code = 400
    code = "BAD_REQUEST"
    default_message = "Bad request"


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"
    default_message = "Not authenticated"


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"
    default_message = "You do not have permission to do this"


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"
    default_message = "Resource not found"


class UpstreamError(AppError):
    status_code = 502
    code = "UPSTREAM_ERROR"
    default_message = "Error contacting DummyJSON"


class UpstreamTimeoutError(UpstreamError):
    status_code = 504
    code = "UPSTREAM_TIMEOUT"
    default_message = "DummyJSON took too long to respond"
