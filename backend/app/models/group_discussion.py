"""The Group Discussion signature feature (Phase 14): one row per GD round,
one-to-one with its InterviewRound (round_type == GROUP_DISCUSSION).
Participants (moderator, 4 AI candidates, the user) are separate rows —
see participant.py."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interview_round import InterviewRound
    from app.models.participant import Participant


class GroupDiscussion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "group_discussions"

    round_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("interview_rounds.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one-to-one with its InterviewRound
    )

    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Full turn-by-turn transcript: [{"speaker": ..., "text": ...,
    # "timestamp": ...}, ...]. Built incrementally by the GD Moderator
    # Agent as the simulation runs (Phase 14) — kept as one JSONB blob
    # rather than a Message table since it's written by one agent, read
    # as a whole for replay/reporting, and never queried per-message.
    transcript: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)

    round: Mapped[InterviewRound] = relationship(back_populates="group_discussion")
    participants: Mapped[list[Participant]] = relationship(
        back_populates="group_discussion", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<GroupDiscussion id={self.id} topic={self.topic!r}>"
