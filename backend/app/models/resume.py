"""Uploaded resume + its parsed representation. Parsing itself is Phase 7;
this model just holds the raw file reference and the eventual parsed JSON."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ResumeStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession
    from app.models.user import User


class Resume(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(
        String(1024), nullable=False, doc="Local path or S3 key — see StorageBackend in Phase 6."
    )

    status: Mapped[ResumeStatus] = mapped_column(
        SAEnum(ResumeStatus, name="resume_status"),
        default=ResumeStatus.UPLOADED,
        nullable=False,
    )

    # Populated by the Resume Agent (Phase 7) — structured output, schema
    # owned by that agent's output contract rather than a rigid DB schema,
    # since resume sections vary a lot and we don't want a migration for
    # every new field the parser learns to extract.
    parsed_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    user: Mapped[User] = relationship(back_populates="resumes")
    interview_sessions: Mapped[list[InterviewSession]] = relationship(back_populates="resume")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Resume id={self.id} filename={self.original_filename!r} status={self.status}>"
