"""
Agent-generated evaluation. A Feedback row is either round-level (overall
assessment of a Technical/HR/Behavioral round, `answer_id` null) or
answer-level (per-answer critique, `answer_id` set). `source` records
which agent produced it, since the Feedback Agent (Phase 15's final
report) synthesizes across every other agent's feedback and needs to
know provenance.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import FeedbackSource
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.answer import Answer
    from app.models.interview_round import InterviewRound


class Feedback(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "feedback"

    round_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("interview_rounds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=True, index=True
    )

    source: Mapped[FeedbackSource] = mapped_column(
        SAEnum(FeedbackSource, name="feedback_source"), nullable=False
    )
    score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Structured breakdown — e.g. {"clarity": 7, "correctness": 8,
    # "strengths": [...], "improvements": [...]}. Shape owned by each
    # agent's output schema (see ai-engine/agents/*/schema), not fixed
    # columns, since every round type scores different dimensions.
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    round: Mapped[InterviewRound] = relationship(back_populates="feedback_entries")
    answer: Mapped[Answer | None] = relationship(back_populates="feedback_entries")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Feedback id={self.id} source={self.source} score={self.score}>"
