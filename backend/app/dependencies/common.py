"""
Shared FastAPI dependencies.

This is the pattern every future dependency (get_current_user,
get_db_session, get_resume_service, ...) follows: a small function that
FastAPI resolves per-request via `Depends(...)`, which routes then take as
a parameter instead of reaching into globals. This is what makes routes
testable — swap `app.dependency_overrides[get_settings]` in a test and
every route that depends on it uses the fake.
"""

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings

# Type alias so route signatures read as `settings: SettingsDep` instead of
# repeating `Annotated[Settings, Depends(get_settings)]` everywhere.
SettingsDep = Annotated[Settings, Depends(get_settings)]
