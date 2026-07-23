# ADR-0004: Database schema — JSONB boundaries, enums, and FK ondelete rules

**Status:** Accepted
**Phase:** 4 — Database

## Context

The 12 tables in the spec (Users, Resumes, JobDescriptions,
InterviewSessions, InterviewRounds, Questions, Answers, Feedback, Reports,
GroupDiscussions, Participants, ActivityLogs) sit at the boundary between
rigid relational structure (who owns what, what belongs to what session)
and AI-agent output that changes shape as agents are iterated on (a
resume's parsed fields, a coding question's test cases, a GD participant's
scoring dimensions). Getting the JSONB-vs-column line wrong in either
direction is expensive: too many rigid columns means a migration every
time an agent's output schema changes; too much JSONB means losing query
performance and referential integrity where it actually matters.

## Decisions

### 1. JSONB only for agent-output payloads whose shape is owned by an agent's schema, not by the DB

Columns like `Resume.parsed_data`, `JobDescription.parsed_requirements`,
`Question.question_metadata`, `Feedback.details`, `Report.learning_roadmap`,
`GroupDiscussion.transcript`, and `Participant.scores` are JSONB because
their shape is defined by an AI agent's structured output schema (see
`ai-engine/agents/*/schema`, built starting Phase 10) — not by this
migration. When the Resume Agent's parser learns to extract a new field,
that's a change to the agent's Pydantic output model, not a database
migration.

Everything else that has real relational meaning — ownership FKs, status
enums, timestamps, scores used for filtering/sorting — is a real column.
`Feedback.score` and `Report.overall_score` are columns (not folded into
`details`/JSONB) specifically because reports and dashboards will sort
and filter by score.

### 2. Enums as Postgres `ENUM` types, not free-text strings or a lookup table

`ResumeStatus`, `InterviewSessionStatus`, `RoundType`, `RoundStatus`,
`ParticipantType`, `FeedbackSource` are all closed, small, rarely-changing
sets — a genuine enum, not a lookup table. Postgres `ENUM` types get
constraint enforcement at the DB level (a typo'd status value is rejected
at insert, not caught later by application code) for a cost of one
migration whenever a new value is added. A lookup table would cost a join
everywhere a status is read/compared to save a rare migration — the wrong
trade for values this stable.

### 3. FK `ondelete` is chosen per relationship, not defaulted uniformly

- `CASCADE`: session → rounds → questions → answers → feedback,
  GD → participants, and `User → {resumes, job_descriptions,
  interview_sessions, activity_logs}`. Deleting the parent should delete
  everything that only exists because of it (GDPR account deletion should
  actually delete a user's data, not orphan it).
- `RESTRICT`: `InterviewSession.resume_id` / `.job_description_id`. A
  Resume or JobDescription that has interview history attached shouldn't
  be deletable while that history still points to it — see the ordering
  note in `interview_session.py`'s inline comment for how this still
  allows full account deletion.
- `SET NULL`: `ActivityLog.user_id`. Audit history should outlive the
  user it's about — deleting a user shouldn't delete the evidence that
  they existed and did things, just anonymize the reference.

### 4. One `Feedback` table for both round-level and answer-level evaluation, not two

A Feedback row always has `round_id`; `answer_id` is set only for
per-answer critique. This avoids two near-identical tables
(`round_feedback`, `answer_feedback`) that the Feedback Agent (Phase 15)
would have to query separately and merge — one table, one `source` enum
recording provenance, is queried once per round.

### 5. Migration written by hand, not via `alembic revision --autogenerate`

This build environment has no network access to a real Postgres instance,
so the initial migration (`alembic/versions/0001_initial_schema.py`) was
hand-written to match every model column-for-column — verified with a
custom script comparing `mapped_column()` fields against the migration's
`sa.Column()` calls (all 12 tables matched with zero diff), but **not**
verified by actually running `alembic upgrade head` against Postgres.
This is a known gap — see `backend/README.md`'s Database section for the
exact commands to verify it for real, and please tell me if anything
fails so it gets fixed before Phase 5 builds on top of it.

## Consequences

- Every future agent-output change (new resume field, new scoring
  dimension) is a Pydantic schema change in `ai-engine/`, not a migration
  — as long as it stays inside an existing JSONB column.
- A new *status value* (e.g. adding a `RoundType`) still requires a
  migration (`ALTER TYPE ... ADD VALUE`) — accepted cost for DB-level
  enforcement.
- Anyone adding a new relationship must consciously choose its `ondelete`
  rather than copy-pasting `CASCADE` everywhere; the three cases above are
  the reference examples to follow.
