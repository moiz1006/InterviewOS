"""
Tests for GET /api/v1/health/ready.

Overrides the DB session dependency with a fake rather than requiring a
real Postgres connection in the test environment — this is the pattern
every future DB-touching endpoint test follows (see
`app/dependencies/db.py`'s docstring).
"""

from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.dependencies.db import get_db_session


class _FakeConnectedSession:
    """Stands in for AsyncSession: `execute()` succeeds, simulating a
    healthy DB connection."""

    async def execute(self, *args: object, **kwargs: object) -> None:
        return None


class _FakeDownSession:
    """Simulates a DB connection failure."""

    async def execute(self, *args: object, **kwargs: object) -> None:
        raise ConnectionError("could not connect to server")


def test_readiness_check_reports_ready_when_db_is_up(app: FastAPI, client: TestClient) -> None:
    async def fake_get_db_session():
        yield _FakeConnectedSession()

    app.dependency_overrides[get_db_session] = fake_get_db_session

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "connected"}


def test_readiness_check_returns_500_when_db_is_down(app: FastAPI, client: TestClient) -> None:
    async def fake_get_db_session():
        yield _FakeDownSession()

    app.dependency_overrides[get_db_session] = fake_get_db_session

    response = client.get("/api/v1/health/ready")

    # Not caught locally — flows through the centralized exception handler
    # (Phase 2) as an unhandled exception, same as any other unexpected
    # failure would.
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_server_error"


def test_readiness_check_calls_execute_on_the_session(app: FastAPI, client: TestClient) -> None:
    fake_session = AsyncMock()

    async def fake_get_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session] = fake_get_db_session

    client.get("/api/v1/health/ready")

    fake_session.execute.assert_awaited_once()
