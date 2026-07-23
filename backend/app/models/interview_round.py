"""One round within an InterviewSession. `round_type` determines which
agent(s) run it (see ai-engine/agents/) and which child rows it has:
Technical/Coding/HR/Behavioral/System-Design rounds have Questions +
Answers; a `group_discussion` round has a GroupDiscussion + Participants
instead."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RoundStatus, RoundType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.feedback import Feedback
    from app.models.group_discussion import GroupDiscussion
    from app.models.interview_session import InterviewSession
    from app.models.question import Question


class InterviewRound(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "interview_rounds"
    __table_args__ = (
        # A session can't have two rounds claiming the same position in
        # its sequence — protects the ordering InterviewPlannerAgent produces.
        UniqueConstraint("session_id", "order_index", name="uq_interview_rounds_session_order"),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    round_type: Mapped[RoundType] = mapped_column(
        SAEnum(RoundType, name="round_type"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[RoundStatus] = mapped_column(
        SAEnum(RoundStatus, name="round_status"), default=RoundStatus.PENDING, nullable=False
    )

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    session: Mapped[InterviewSession] = relationship(back_populates="rounds")
    questions: Mapped[list[Question]] = relationship(
        back_populates="round", cascade="all, delete-orphan", order_by="Question.order_index"
    )
    feedback_entries: Mapped[list[Feedback]] = relationship(
        back_populates="round", cascade="all, delete-orphan"
    )
    group_discussion: Mapped[GroupDiscussion | None] = relationship(
        back_populates="round", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<InterviewRound id={self.id} type={self.round_type} status={self.status}>"
