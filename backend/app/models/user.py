"""User account. Auth fields (password hash, verification/reset tokens
handled as separate columns rather than a joined table, since they're
always accessed alongside the user) — full auth logic lands in Phase 5."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.activity_log import ActivityLog
    from app.models.interview_session import InterviewSession
    from app.models.job_description import JobDescription
    from app.models.resume import Resume


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    resumes: Mapped[list[Resume]] = relationship(back_populates="user", cascade="all, delete-orphan")
    job_descriptions: Mapped[list[JobDescription]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    interview_sessions: Mapped[list[InterviewSession]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    activity_logs: Mapped[list[ActivityLog]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug convenience only
        return f"<User id={self.id} email={self.email!r}>"
