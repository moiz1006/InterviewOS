"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-20 00:00:00

Creates all 12 tables from the spec (Users, Resumes, JobDescriptions,
InterviewSessions, InterviewRounds, Questions, Answers, Feedback, Reports,
GroupDiscussions, Participants, ActivityLogs) in FK-dependency order.

NOTE ON HOW THIS WAS WRITTEN: this sandbox has no network access, so this
migration could not be produced with `alembic revision --autogenerate`
against a real Postgres instance, nor verified with `alembic upgrade
head`. It was hand-written to match `app/models/*.py` column-for-column,
constraint-for-constraint, and cross-checked against the naming
convention in `app/db/base.py` so a *real* autogenerate run later
produces an empty diff instead of fighting this migration. Please run
`alembic upgrade head` against a real Postgres locally and tell me if
anything doesn't match — see backend/README.md's Database section.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------
    # users
    # ---------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ---------------------------------------------------------------
    # resumes
    # ---------------------------------------------------------------
    resume_status = postgresql.ENUM(
        "uploaded", "parsing", "parsed", "failed", name="resume_status"
    )
    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("status", resume_status, nullable=False, server_default="uploaded"),
        sa.Column("parsed_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_resumes"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_resumes_user_id_users", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])

    # ---------------------------------------------------------------
    # job_descriptions
    # ---------------------------------------------------------------
    op.create_table(
        "job_descriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("role_title", sa.String(length=255), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("parsed_requirements", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_job_descriptions"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_job_descriptions_user_id_users", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_job_descriptions_user_id", "job_descriptions", ["user_id"])

    # ---------------------------------------------------------------
    # interview_sessions
    # ---------------------------------------------------------------
    interview_session_status = postgresql.ENUM(
        "planned", "in_progress", "completed", "abandoned", name="interview_session_status"
    )
    op.create_table(
        "interview_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_description_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status", interview_session_status, nullable=False, server_default="planned"
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_interview_sessions"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_interview_sessions_user_id_users", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["resume_id"],
            ["resumes.id"],
            name="fk_interview_sessions_resume_id_resumes",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["job_description_id"],
            ["job_descriptions.id"],
            name="fk_interview_sessions_job_description_id_job_descriptions",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_interview_sessions_user_id", "interview_sessions", ["user_id"])

    # ---------------------------------------------------------------
    # interview_rounds
    # ---------------------------------------------------------------
    round_type = postgresql.ENUM(
        "hr", "technical", "coding", "system_design", "behavioral", "group_discussion",
        name="round_type",
    )
    round_status = postgresql.ENUM(
        "pending", "in_progress", "completed", "skipped", name="round_status"
    )
    op.create_table(
        "interview_rounds",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("round_type", round_type, nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("status", round_status, nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_interview_rounds"),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["interview_sessions.id"],
            name="fk_interview_rounds_session_id_interview_sessions",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "session_id", "order_index", name="uq_interview_rounds_session_order"
        ),
    )
    op.create_index("ix_interview_rounds_session_id", "interview_rounds", ["session_id"])

    # ---------------------------------------------------------------
    # questions
    # ---------------------------------------------------------------
    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("round_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("question_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_questions"),
        sa.ForeignKeyConstraint(
            ["round_id"],
            ["interview_rounds.id"],
            name="fk_questions_round_id_interview_rounds",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_questions_round_id", "questions", ["round_id"])

    # ---------------------------------------------------------------
    # answers
    # ---------------------------------------------------------------
    op.create_table(
        "answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("audio_url", sa.String(length=1024), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_answers"),
        sa.ForeignKeyConstraint(
            ["question_id"], ["questions.id"], name="fk_answers_question_id_questions", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_answers_question_id", "answers", ["question_id"])

    # ---------------------------------------------------------------
    # feedback
    # ---------------------------------------------------------------
    feedback_source = postgresql.ENUM(
        "recruiter_agent",
        "technical_agent",
        "coding_agent",
        "behavior_agent",
        "gd_moderator_agent",
        "feedback_agent",
        name="feedback_source",
    )
    op.create_table(
        "feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("round_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("answer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source", feedback_source, nullable=False),
        sa.Column("score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_feedback"),
        sa.ForeignKeyConstraint(
            ["round_id"],
            ["interview_rounds.id"],
            name="fk_feedback_round_id_interview_rounds",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["answer_id"], ["answers.id"], name="fk_feedback_answer_id_answers", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_feedback_round_id", "feedback", ["round_id"])
    op.create_index("ix_feedback_answer_id", "feedback", ["answer_id"])

    # ---------------------------------------------------------------
    # reports
    # ---------------------------------------------------------------
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("overall_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("strengths_weaknesses", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("learning_roadmap", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_reports"),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["interview_sessions.id"],
            name="fk_reports_session_id_interview_sessions",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("session_id", name="uq_reports_session_id"),
    )

    # ---------------------------------------------------------------
    # group_discussions
    # ---------------------------------------------------------------
    op.create_table(
        "group_discussions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("round_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("topic", sa.String(length=500), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("transcript", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_group_discussions"),
        sa.ForeignKeyConstraint(
            ["round_id"],
            ["interview_rounds.id"],
            name="fk_group_discussions_round_id_interview_rounds",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("round_id", name="uq_group_discussions_round_id"),
    )

    # ---------------------------------------------------------------
    # participants
    # ---------------------------------------------------------------
    participant_type = postgresql.ENUM(
        "user", "ai_moderator", "ai_candidate", name="participant_type"
    )
    op.create_table(
        "participants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("group_discussion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("participant_type", participant_type, nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("persona", sa.String(length=100), nullable=True),
        sa.Column("scores", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_participants"),
        sa.ForeignKeyConstraint(
            ["group_discussion_id"],
            ["group_discussions.id"],
            name="fk_participants_group_discussion_id_group_discussions",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_participants_group_discussion_id", "participants", ["group_discussion_id"])

    # ---------------------------------------------------------------
    # activity_logs
    # ---------------------------------------------------------------
    op.create_table(
        "activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("log_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_activity_logs"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_activity_logs_user_id_users", ondelete="SET NULL"
        ),
    )
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"])
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"])


def downgrade() -> None:
    # Reverse FK-dependency order.
    op.drop_index("ix_activity_logs_action", table_name="activity_logs")
    op.drop_index("ix_activity_logs_user_id", table_name="activity_logs")
    op.drop_table("activity_logs")

    op.drop_index("ix_participants_group_discussion_id", table_name="participants")
    op.drop_table("participants")
    postgresql.ENUM(name="participant_type").drop(op.get_bind(), checkfirst=True)

    op.drop_table("group_discussions")

    op.drop_table("reports")

    op.drop_index("ix_feedback_answer_id", table_name="feedback")
    op.drop_index("ix_feedback_round_id", table_name="feedback")
    op.drop_table("feedback")
    postgresql.ENUM(name="feedback_source").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_answers_question_id", table_name="answers")
    op.drop_table("answers")

    op.drop_index("ix_questions_round_id", table_name="questions")
    op.drop_table("questions")

    op.drop_index("ix_interview_rounds_session_id", table_name="interview_rounds")
    op.drop_table("interview_rounds")
    postgresql.ENUM(name="round_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="round_type").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_interview_sessions_user_id", table_name="interview_sessions")
    op.drop_table("interview_sessions")
    postgresql.ENUM(name="interview_session_status").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_job_descriptions_user_id", table_name="job_descriptions")
    op.drop_table("job_descriptions")

    op.drop_index("ix_resumes_user_id", table_name="resumes")
    op.drop_table("resumes")
    postgresql.ENUM(name="resume_status").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
