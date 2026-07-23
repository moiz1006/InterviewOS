"""
Shared mixins so every model gets a UUID primary key and timestamp columns
the same way, instead of each model file redefining them slightly
differently.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKeyMixin:
    """
    UUID (not auto-incrementing integer) primary keys throughout, per the
    project's database rules. UUIDs are generated application-side
    (`default=uuid.uuid4`) rather than relying on a Postgres extension
    (`gen_random_uuid()`), which keeps the ID available on the Python
    object immediately after construction — useful for building related
    objects (e.g. a Resume and its ActivityLog entry) in the same
    transaction before either is flushed to the DB.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """`created_at` / `updated_at`, both DB-generated so they're correct
    even for rows inserted outside the ORM (e.g. a manual migration)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
