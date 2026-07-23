"""Pasted job description + its parsed requirements (JD Analyzer Agent,
Phase 9 fills `parsed_requirements`)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession
    from app.models.user import User


class JobDescription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "job_descriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Populated by the JD Analyzer Agent — extracted must-have/nice-to-have
    # skills, seniority level, etc. Same JSONB rationale as Resume.parsed_data.
    parsed_requirements: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    user: Mapped[User] = relationship(back_populates="job_descriptions")
    interview_sessions: Mapped[list[InterviewSession]] = relationship(
        back_populates="job_description"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<JobDescription id={self.id} role={self.role_title!r} company={self.company_name!r}>"
