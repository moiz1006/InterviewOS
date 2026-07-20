"""
Application factory.

`create_app()` is the single place that wires together settings, logging,
middleware (in order — order matters, see comments below), exception
handlers, and routers. Using a factory instead of a module-level `app =
FastAPI()` means tests can build a fresh app with overridden settings
instead of importing a singleton configured for one environment.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging, get_logger
from app.middleware.exception_handler import register_exception_handlers
from app.middleware.request_id import RequestContextMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

logger = get_logger(__name__)


def _build_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        logger.info("app_startup", app_name=settings.app_name, environment=settings.environment)
        yield
        logger.info("app_shutdown", app_name=settings.app_name)

    return lifespan


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        lifespan=_build_lifespan(settings),
    )

    # Middleware executes in reverse registration order for requests
    # (last added runs first), and in registration order for responses.
    # We want, on the way in: CORS -> security headers -> request context.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
