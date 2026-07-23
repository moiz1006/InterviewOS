"""One participant in a GroupDiscussion: the real user, the moderator, or
one of the 4 AI candidates (each with a distinct persona — aggressive,
introvert, data-driven, excellent communicator, per the spec). Scoring
dimensions (leadership, confidence, communication, speaking_time,
interruptions, logic, relevance) live in `scores` as JSONB rather than
seven columns, since the Moderator Agent may add dimensions over time
without a migration."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ParticipantType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.group_discussion import GroupDiscussion


class Participant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "participants"

    group_discussion_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("group_discussions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    participant_type: Mapped[ParticipantType] = mapped_column(
        SAEnum(ParticipantType, name="participant_type"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # e.g. "aggressive", "introvert", "data_driven", "excellent_communicator"
    # for AI candidates; null for the real user and the moderator.
    persona: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # {"leadership": 7, "confidence": 8, "communication": 9,
    #  "speaking_time_seconds": 145, "interruptions": 2, "logic": 8,
    #  "relevance": 9} — per the Moderator's scoring dimensions in the spec.
    scores: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    group_discussion: Mapped[GroupDiscussion] = relationship(back_populates="participants")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Participant id={self.id} type={self.participant_type} name={self.display_name!r}>"
