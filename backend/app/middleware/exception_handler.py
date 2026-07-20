"""
Centralized exception handling.

Every error, whether it's an expected `AppException` raised by a service,
a request validation failure, or a genuinely unexpected bug, is caught
here and turned into one consistent JSON error shape:

    {"error": {"code": "...", "message": "...", "details": {...}}}

so frontend error handling never has to guess the shape of an error
response. Unexpected exceptions are logged with a stack trace and returned
to the client as a generic 500 — internal details are never leaked into
the response body.
"""

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppException,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitedError,
    UnauthorizedError,
    UpstreamServiceError,
    ValidationError,
)

logger = structlog.get_logger(__name__)

_STATUS_BY_EXCEPTION: dict[type[AppException], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    ConflictError: status.HTTP_409_CONFLICT,
    RateLimitedError: status.HTTP_429_TOO_MANY_REQUESTS,
    UpstreamServiceError: status.HTTP_502_BAD_GATEWAY,
}


def _error_body(code: str, message: str, details: dict | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or {}}}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to the app. Called once from `app/main.py`."""

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        status_code = _STATUS_BY_EXCEPTION.get(type(exc), status.HTTP_400_BAD_REQUEST)
        logger.warning(
            "app_exception",
            code=exc.code,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=status_code,
            content=_error_body(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("request_validation_error", errors=exc.errors(), path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(
                "request_validation_error",
                "The request body failed validation.",
                {"errors": exc.errors()},
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            path=request.url.path,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(
                "internal_server_error",
                "Something went wrong on our end. Please try again.",
            ),
        )
