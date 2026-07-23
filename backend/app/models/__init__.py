"""
SQLAlchemy ORM models.

Every model MUST be imported here. Two reasons:
  1. Alembic's `env.py` imports `Base.metadata` from this package to diff
     against the database — a model that's never imported never
     registers itself on `Base.metadata`, so autogenerate would silently
     ignore its table entirely.
  2. `relationship()` calls elsewhere use forward-reference strings
     (e.g. `Mapped["Resume"]`) that SQLAlchemy resolves lazily against
     its mapper registry — which only has entries for classes that have
     actually been imported somewhere by the time mappers are configured.
"""

from app.db.base import Base
from app.models.activity_log import ActivityLog
from app.models.answer import Answer
from app.models.feedback import Feedback
from app.models.group_discussion import GroupDiscussion
from app.models.interview_round import InterviewRound
from app.models.interview_session import InterviewSession
from app.models.job_description import JobDescription
from app.models.participant import Participant
from app.models.question import Question
from app.models.report import Report
from app.models.resume import Resume
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "Resume",
    "JobDescription",
    "InterviewSession",
    "InterviewRound",
    "Question",
    "Answer",
    "Feedback",
    "Report",
    "GroupDiscussion",
    "Participant",
    "ActivityLog",
]
