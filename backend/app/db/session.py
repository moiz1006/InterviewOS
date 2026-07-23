"""
Async database engine and session management.

One process-wide async engine (connection-pooled), and a session factory
that hands out a fresh `AsyncSession` per request via `get_db_session`
(see `app/dependencies/db.py`). Routes never construct a session
themselves — they depend on `DbSessionDep`, which guarantees the session
is closed (and rolled back on error) at the end of the request regardless
of what the route does.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings


def create_engine(settings: Settings | None = None) -> AsyncEngine:
    settings = settings or get_settings()
    return create_async_engine(
        settings.database_url,
        echo=settings.db_echo,
        pool_pre_ping=True,  # avoids serving a dead connection after a DB restart/failover
        future=True,
    )


# Process-wide singleton engine + session factory. A factory function
# (`create_engine`) still exists above so tests can build an isolated
# engine against a different `DATABASE_URL` without touching this global.
engine: AsyncEngine = create_engine()
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # objects stay usable after commit, e.g. returning them in a response
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: yields a session, commits on clean exit, rolls back
    and re-raises on any exception, always closes. Services should call
    `session.flush()` when they need generated PKs before commit, but
    should NOT call `session.commit()` themselves — the request boundary
    (this function) owns the transaction boundary, so one request is one
    transaction unless a service explicitly opts into nested savepoints.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
