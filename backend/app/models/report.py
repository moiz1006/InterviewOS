"""The final report (Phase 15) synthesized by the Feedback Agent across
every round's Feedback rows, plus the Learning Roadmap (Phase 16) built
from it. One-to-one with InterviewSession — enforced by the unique
constraint on session_id, not just by convention."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession


class Report(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "reports"

    session_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # enforces the one-to-one at the DB level
    )

    overall_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # {"strengths": [...], "weaknesses": [...], "per_round_breakdown": {...}}
    strengths_weaknesses: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Career Coach Agent's structured output: ordered topics/resources/
    # milestones. Shape owned by that agent, not fixed columns — see
    # ai-engine/agents/career_coach_agent/.
    learning_roadmap: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    session: Mapped[InterviewSession] = relationship(back_populates="report")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Report id={self.id} session_id={self.session_id} score={self.overall_score}>"
