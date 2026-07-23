"""
Declarative base for all ORM models.

The naming convention is the important part of this file: without it,
SQLAlchemy lets the database driver pick constraint names (e.g.
Postgres auto-names a unique constraint `resumes_user_id_key`), which
means Alembic's autogenerate produces a *different* migration depending
on what the DB happened to name things last time, and `DROP CONSTRAINT`/
`ALTER` migrations become unwritable by hand because you can't predict
the name. Fixing this after the fact means renaming every constraint in
production — so it's set up here, before the first migration, once.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Every model in `app/models/` inherits from this."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
