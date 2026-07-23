"""Generic audit trail: login, resume upload, session started/completed,
etc. Deliberately generic (`action` + `metadata` JSONB) rather than one
table per event type, since this is written far more often than it's
queried in structured ways — structured per-domain history belongs on the
domain tables themselves (e.g. InterviewSession.status transitions)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class ActivityLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "activity_logs"

    # Nullable: some actions worth logging (e.g. a failed login attempt
    # with an unrecognized email) don't have a resolvable user yet.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    log_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    user: Mapped[User | None] = relationship(back_populates="activity_logs")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ActivityLog id={self.id} action={self.action!r}>"
