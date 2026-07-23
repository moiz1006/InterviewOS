"""The candidate's (user's) answer to a Question. `audio_url` supports the
Voice Interview feature (Phase 13) — text-only answers leave it null."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.feedback import Feedback
    from app.models.question import Question


class Answer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "answers"

    question_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    audio_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    question: Mapped[Question] = relationship(back_populates="answers")
    feedback_entries: Mapped[list[Feedback]] = relationship(
        back_populates="answer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Answer id={self.id} question_id={self.question_id}>"
