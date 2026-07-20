"""
Application configuration.

Single source of truth for every environment-driven setting. Nothing else
in the codebase should call `os.environ` directly — import `get_settings()`
instead. This keeps config testable (override via `.dependency_overrides`
in tests) and makes the full set of required env vars discoverable in one
place instead of scattered across the codebase.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Typed, validated application settings.

    Values are read from environment variables (or a `.env` file in local
    dev). See `/.env.example` at the repo root for the full documented
    list, including vars that later phases (DB, auth, AI providers) will
    add here.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # tolerate unrelated vars (e.g. frontend-only ones) in a shared .env
    )

    # --- App ---
    app_name: str = "InterviewOS"
    environment: Literal["development", "staging", "production", "test"] = "development"
    api_v1_prefix: str = "/api/v1"
    debug: bool = Field(default=False)

    # --- CORS ---
    backend_cors_origins: list[str] = ["http://localhost:3000"]

    # --- Logging ---
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_json: bool = Field(
        default=True,
        description="JSON logs in production/staging; human-readable in local dev.",
    )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor.

    `lru_cache` gives us a process-wide singleton without a global variable
    — settings are read from the environment exactly once per process, and
    FastAPI's dependency system can still override it cleanly in tests via
    `app.dependency_overrides[get_settings] = lambda: test_settings`.
    """
    return Settings()
