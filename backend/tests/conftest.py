"""Shared pytest fixtures."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    """Isolated settings for tests — never touches a real .env file's values we don't expect."""
    return Settings(environment="test", log_json=False)


@pytest.fixture
def app(test_settings: Settings) -> FastAPI:
    """The FastAPI app instance, exposed separately from `client` so tests
    can set `app.dependency_overrides[...]` before constructing the
    client — needed for endpoints like `/health/ready` that depend on a
    real DB connection we don't have in the test environment."""
    return create_app(settings=test_settings)


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)
