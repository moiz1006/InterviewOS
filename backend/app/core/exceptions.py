"""
Application exception hierarchy.

Services and repositories raise these instead of returning error codes or
raising bare `Exception`/`HTTPException` directly. Keeping exceptions
framework-agnostic (no FastAPI import here) means `services/` and
`repositories/` don't depend on the web layer — they could be reused from a
Celery task or a CLI script just as easily. The mapping from these
exceptions to HTTP status codes lives entirely in
`app/middleware/exception_handler.py`.
"""

from typing import Any


class AppException(Exception):
    """
    Base class for all application-raised (i.e. expected/handled) errors.

    Attributes:
        message: human-readable error message, safe to show to API clients.
        code: short, stable machine-readable error code (e.g.
              "resume_not_found") — frontends can switch on this without
              parsing message strings, which may change wording over time.
        details: optional structured extra context (e.g. field-level
                  validation errors).
    """

    def __init__(
        self,
        message: str,
        *,
        code: str = "app_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    """Requested resource does not exist. Maps to HTTP 404."""

    def __init__(self, message: str = "Resource not found", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "not_found"), **kwargs)


class ValidationError(AppException):
    """Request failed a business-rule validation. Maps to HTTP 422."""

    def __init__(self, message: str = "Validation failed", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "validation_error"), **kwargs)


class UnauthorizedError(AppException):
    """Missing or invalid credentials. Maps to HTTP 401."""

    def __init__(self, message: str = "Not authenticated", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "unauthorized"), **kwargs)


class ForbiddenError(AppException):
    """Authenticated but not permitted. Maps to HTTP 403."""

    def __init__(self, message: str = "Not permitted", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "forbidden"), **kwargs)


class ConflictError(AppException):
    """Request conflicts with current state (e.g. duplicate email). Maps to HTTP 409."""

    def __init__(self, message: str = "Conflict", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "conflict"), **kwargs)


class RateLimitedError(AppException):
    """Caller exceeded a rate limit. Maps to HTTP 429."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "rate_limited"), **kwargs)


class UpstreamServiceError(AppException):
    """
    A dependency we call (AI provider, email service, S3, ...) failed.
    Maps to HTTP 502. Distinct from AppException's other subclasses because
    it's not the caller's fault — useful for retry/alerting logic later.
    """

    def __init__(self, message: str = "Upstream service error", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "upstream_error"), **kwargs)
