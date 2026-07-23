"""Database session dependency — see app/db/session.py for the transaction
boundary semantics this wraps."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session

DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
