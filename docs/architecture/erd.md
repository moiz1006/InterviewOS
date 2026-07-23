# Entity-Relationship Diagram

Generated from `backend/app/models/`. See
[`ADR-0004-database-schema.md`](ADR-0004-database-schema.md) for the
reasoning behind the JSONB fields, enum choices, and FK ondelete rules.

```mermaid
erDiagram
    USERS ||--o{ RESUMES : uploads
    USERS ||--o{ JOB_DESCRIPTIONS : pastes
    USERS ||--o{ INTERVIEW_SESSIONS : runs
    USERS ||--o{ ACTIVITY_LOGS : generates

    RESUMES ||--o{ INTERVIEW_SESSIONS : "used in"
    JOB_DESCRIPTIONS ||--o{ INTERVIEW_SESSIONS : "used in"

    INTERVIEW_SESSIONS ||--o{ INTERVIEW_ROUNDS : contains
    INTERVIEW_SESSIONS ||--o| REPORTS : produces

    INTERVIEW_ROUNDS ||--o{ QUESTIONS : contains
    INTERVIEW_ROUNDS ||--o{ FEEDBACK : "scored by"
    INTERVIEW_ROUNDS ||--o| GROUP_DISCUSSIONS : "is a"

    QUESTIONS ||--o{ ANSWERS : has

    ANSWERS ||--o{ FEEDBACK : "scored by"

    GROUP_DISCUSSIONS ||--o{ PARTICIPANTS : has

    USERS {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        bool is_active
        bool is_verified
    }
    RESUMES {
        uuid id PK
        uuid user_id FK
        string original_filename
        string storage_path
        enum status
        jsonb parsed_data
    }
    JOB_DESCRIPTIONS {
        uuid id PK
        uuid user_id FK
        string company_name
        string role_title
        text raw_text
        jsonb parsed_requirements
    }
    INTERVIEW_SESSIONS {
        uuid id PK
        uuid user_id FK
        uuid resume_id FK
        uuid job_description_id FK
        enum status
        timestamp completed_at
    }
    INTERVIEW_ROUNDS {
        uuid id PK
        uuid session_id FK
        enum round_type
        int order_index
        enum status
    }
    QUESTIONS {
        uuid id PK
        uuid round_id FK
        text prompt
        int order_index
        jsonb question_metadata
    }
    ANSWERS {
        uuid id PK
        uuid question_id FK
        text content
        string audio_url
        timestamp submitted_at
    }
    FEEDBACK {
        uuid id PK
        uuid round_id FK
        uuid answer_id FK "nullable"
        enum source
        numeric score
        text summary
        jsonb details
    }
    REPORTS {
        uuid id PK
        uuid session_id FK UK
        numeric overall_score
        text summary
        jsonb strengths_weaknesses
        jsonb learning_roadmap
    }
    GROUP_DISCUSSIONS {
        uuid id PK
        uuid round_id FK UK
        string topic
        int duration_seconds
        jsonb transcript
    }
    PARTICIPANTS {
        uuid id PK
        uuid group_discussion_id FK
        enum participant_type
        string display_name
        string persona
        jsonb scores
    }
    ACTIVITY_LOGS {
        uuid id PK
        uuid user_id FK "nullable"
        string action
        inet ip_address
        jsonb log_metadata
    }
```
