"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    """Isolated settings for tests — never touches a real .env file's values we don't expect."""
    return Settings(environment="test", log_json=False)


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    app = create_app(settings=test_settings)
    return TestClient(app)
