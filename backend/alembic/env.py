"""
Alembic environment.

Two things this must get right:
  1. The DB URL comes from `app.core.config.get_settings()` — the exact
     same Settings object the running app uses — not a second copy in
     alembic.ini. One source of truth for "what database are we talking
     to."
  2. `target_metadata` is `Base.metadata` from `app.models`, which (by
     importing every model in `app/models/__init__.py`) has every table
     registered. Import `app.models` here, not individual model files —
     importing a subset would make autogenerate silently blind to
     whatever wasn't imported.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config

from app.core.config import get_settings
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return get_settings().database_url


def run_migrations_offline() -> None:
    """`alembic upgrade head --sql` — emits SQL without a DB connection."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Normal `alembic upgrade head` — runs against a live async connection."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable: AsyncEngine = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # migrations are a one-shot script, not a long-lived pool
    )

    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
