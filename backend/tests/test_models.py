"""
Tests for the model layer itself, independent of a real database
connection.

`configure_mappers()` is the important one: it forces SQLAlchemy to
resolve every `relationship()`'s forward-reference string against the
mapper registry right now, at test time, instead of lazily the first time
that relationship is touched in production. A typo'd `back_populates` or
a model that forgot to get imported into `app/models/__init__.py` fails
here, loudly, instead of surfacing as a confusing runtime error deep in a
service months from now.
"""

from sqlalchemy.orm import configure_mappers

from app.models import Base

EXPECTED_TABLES = {
    "users",
    "resumes",
    "job_descriptions",
    "interview_sessions",
    "interview_rounds",
    "questions",
    "answers",
    "feedback",
    "reports",
    "group_discussions",
    "participants",
    "activity_logs",
}


def test_all_expected_tables_are_registered() -> None:
    assert set(Base.metadata.tables.keys()) == EXPECTED_TABLES


def test_mappers_configure_without_error() -> None:
    """Resolves every relationship() forward reference. Raises
    sqlalchemy.exc.InvalidRequestError if any back_populates pair is
    missing or mismatched, or if a related class was never imported."""
    configure_mappers()


def test_naming_convention_is_applied_to_every_table() -> None:
    """Every table's primary key constraint should follow pk_<table>,
    confirming app/db/base.py's naming convention is actually in effect
    (not just present in the file but unused)."""
    for table_name, table in Base.metadata.tables.items():
        assert table.primary_key.name == f"pk_{table_name}"
