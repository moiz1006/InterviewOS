"""
One InterviewSession = one full run of the platform for a given
(user, resume, job description) triple: ATS score -> skill gap -> planned
rounds -> final report. `InterviewRound` rows are the individual HR/
technical/coding/system-design/behavioral/GD steps within it.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import InterviewSessionStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interview_round import InterviewRound
    from app.models.job_description import JobDescription
    from app.models.report import Report
    from app.models.resume import Resume
    from app.models.user import User


class InterviewSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "interview_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("resumes.id", ondelete="RESTRICT"), nullable=False
    )
    job_description_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="RESTRICT"), nullable=False
    )
    # RESTRICT (not CASCADE) on resume/JD: a Resume or JobDescription that
    # has interview history shouldn't be deletable out from under it. Full
    # account deletion still works because SQLAlchemy's unit-of-work
    # deletes User.interview_sessions (cascaded) before User.resumes
    # (also cascaded) in the same flush — RESTRICT only blocks deleting a
    # Resume/JD *while a session still references it*, which is exactly
    # the case we want to prevent.

    status: Mapped[InterviewSessionStatus] = mapped_column(
        SAEnum(InterviewSessionStatus, name="interview_session_status"),
        default=InterviewSessionStatus.PLANNED,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="interview_sessions")
    resume: Mapped[Resume] = relationship(back_populates="interview_sessions")
    job_description: Mapped[JobDescription] = relationship(back_populates="interview_sessions")

    rounds: Mapped[list[InterviewRound]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewRound.order_index",
    )
    report: Mapped[Report | None] = relationship(
        back_populates="session", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<InterviewSession id={self.id} status={self.status}>"
