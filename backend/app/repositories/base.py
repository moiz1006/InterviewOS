"""
Generic repository base class.

Every domain repository (created starting Phase 5 — `UserRepository`,
`ResumeRepository`, ...) subclasses this instead of hand-writing the same
`get`/`get_multi`/`create`/`update`/`delete` boilerplate. Services depend
on repositories, never on `AsyncSession` directly — that's what keeps
`services/` testable with an in-memory fake repository instead of a real
database.
"""

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Parameterize with a model: `class ResumeRepository(BaseRepository[Resume]): ...`

    Deliberately thin — this is CRUD only. Query logic specific to one
    domain (e.g. "resumes with a pending ATS score older than 5 minutes")
    belongs as a named method on that domain's own repository subclass,
    not as a generic filter DSL bolted onto this base.
    """

    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: uuid.UUID) -> ModelType | None:
        return await self.session.get(self.model, id)

    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> list[ModelType]:
        result = await self.session.execute(select(self.model).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def create(self, **fields: Any) -> ModelType:
        instance = self.model(**fields)
        self.session.add(instance)
        await self.session.flush()  # populate generated defaults (id, created_at) without committing
        return instance

    async def update(self, instance: ModelType, **fields: Any) -> ModelType:
        for key, value in fields.items():
            setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.flush()
