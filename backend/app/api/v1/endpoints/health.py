"""
Health check endpoint.

Deliberately the only concrete business endpoint in Phase 2 — everything
else here (auth, resumes, interviews, ...) lands in later phases. This one
exists now so we have something end-to-end to verify the skeleton with:
routing, DI, structured logging, and the app factory all get exercised by
one real request.
"""

from fastapi import APIRouter

from app.dependencies.common import SettingsDep
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness/readiness check",
    tags=["system"],
)
async def health_check(settings: SettingsDep) -> HealthResponse:
    """
    Returns 200 with basic app metadata if the process is up.

    This does NOT check downstream dependencies (DB, Redis, ...) yet —
    that's added in Phase 4 once those dependencies exist, as a separate
    `/health/ready` distinct from this liveness check.
    """
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.environment,
    )
