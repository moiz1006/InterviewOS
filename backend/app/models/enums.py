"""
Enums shared across models. Defined once here (not inline per-model) so
`app/schemas/` and `ai-engine/` can import the same enum instead of
re-declaring string literals that can drift out of sync with the DB.
"""

import enum


class ResumeStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"


class InterviewSessionStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class RoundType(str, enum.Enum):
    HR = "hr"
    TECHNICAL = "technical"
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"
    GROUP_DISCUSSION = "group_discussion"


class RoundStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class ParticipantType(str, enum.Enum):
    USER = "user"
    AI_MODERATOR = "ai_moderator"
    AI_CANDIDATE = "ai_candidate"


class FeedbackSource(str, enum.Enum):
    """Which agent produced a given Feedback row — see ai-engine/agents/."""

    RECRUITER_AGENT = "recruiter_agent"
    TECHNICAL_AGENT = "technical_agent"
    CODING_AGENT = "coding_agent"
    BEHAVIOR_AGENT = "behavior_agent"
    GD_MODERATOR_AGENT = "gd_moderator_agent"
    FEEDBACK_AGENT = "feedback_agent"
