"""
Health check endpoints.

Two distinct checks, deliberately not merged into one:
  - `/health` — liveness: is the process up at all? Never touches the DB.
    A load balancer or orchestrator uses this to decide whether to kill
    and restart the process.
  - `/health/ready` — readiness: can this process actually serve traffic?
    Checks the DB connection. An orchestrator uses this to decide whether
    to route traffic to the process — a process can be alive but not
    ready (e.g. DB briefly unreachable) without needing a restart.
"""

from fastapi import APIRouter
from sqlalchemy import text

from app.dependencies.common import SettingsDep
from app.dependencies.db import DbSessionDep
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness check",
    tags=["system"],
)
async def health_check(settings: SettingsDep) -> HealthResponse:
    """Returns 200 if the process is up. Does not check downstream
    dependencies — see `/health/ready` for that."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.environment,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness check (verifies DB connectivity)",
    tags=["system"],
)
async def readiness_check(db: DbSessionDep) -> ReadinessResponse:
    """
    Runs `SELECT 1` against the real database connection pool. If this
    fails, FastAPI's centralized exception handler (Phase 2) turns it into
    a 500 with our standard error envelope — deliberately not caught here,
    since "the DB is down" should be loud, not swallowed into a false
    "ready" response.
    """
    await db.execute(text("SELECT 1"))
    return ReadinessResponse(status="ready", database="connected")

