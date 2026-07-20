# InterviewOS

**InterviewOS** is an AI-powered recruitment simulation platform. Given a resume
and a job description, it runs an end-to-end interview-preparation workflow —
resume parsing, ATS scoring, skill-gap analysis, multi-round mock interviews
(HR, technical, coding, system design, behavioral, group discussion), and a
final report with a personalized learning roadmap.

It is **not** a chatbot. It is a workflow of specialized, independently
defined AI agents (resume parsing, ATS scoring, JD analysis, interview
planning, each interview round, group-discussion moderation, feedback
synthesis, career coaching), each with its own system prompt, memory scope,
tool access, structured output schema, and evaluation criteria.

---

## Status

🚧 **Phase 2 — Backend Structure** (this commit)

See [`docs/architecture/00-roadmap.md`](docs/architecture/00-roadmap.md) for
the full 19-phase build plan and current progress.

---

## Monorepo layout

```
InterviewOS/
├── frontend/         Next.js + TypeScript app (App Router, Shadcn UI)
├── backend/           FastAPI service — clean architecture, REST API
├── ai-engine/          LangGraph agent graphs, providers, tools, evals
├── docs/                Architecture, ADRs, API reference
├── infrastructure/       Docker, Nginx, environment configs
├── scripts/                Dev/ops helper scripts
└── .github/workflows/       CI/CD pipelines
```

Each top-level directory is its own concern with its own dependency
manifest — this is a monorepo, not a single deployable unit. See
`docs/architecture/` for the rationale (ADR-0001).

## Why this structure

- **`frontend/` and `backend/` are fully decoupled.** They communicate only
  over the versioned REST API (`/api/v1/...`). Either can be deployed,
  scaled, or replaced independently.
- **`ai-engine/` is separate from `backend/`.** Agent graphs, prompts, and
  provider routing change at a different pace and for different reasons than
  CRUD/API code, and may need different scaling characteristics (long-running
  LLM calls vs. fast request/response). Phase 10 covers how `backend/`
  invokes `ai-engine/` (in-process import vs. internal service — decided
  with a documented ADR, not by default).
- **`docs/` holds Architecture Decision Records (ADRs)**, not just
  after-the-fact documentation. Every non-trivial structural choice in this
  project gets a numbered ADR before code is written.

## Getting started

Only the backend is runnable so far (Phase 3 adds the frontend).

```bash
make backend-install
make backend-run     # http://localhost:8000/docs
make backend-test
```

See [`backend/README.md`](backend/README.md) for full details, or
[`docs/architecture/ADR-0002-backend-package-layout.md`](docs/architecture/ADR-0002-backend-package-layout.md)
for why it's structured the way it is.

## Development process

This project is built **phase by phase**, not all at once. Each phase:

1. States the architecture and the reasoning behind it (usually an ADR).
2. Ships production-quality code for that slice only.
3. Explains how to test/verify that slice.
4. Waits for review before the next phase starts.

Current phase and full roadmap: [`docs/architecture/00-roadmap.md`](docs/architecture/00-roadmap.md).

## Tech stack

| Layer      | Choices |
|------------|---------|
| Frontend   | Next.js, React, TypeScript, TailwindCSS, Shadcn UI, TanStack Query, Zustand, React Hook Form, Zod |
| Backend    | FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, Celery, WebSockets |
| AI Engine  | LangGraph, pgvector, multi-provider router (OpenAI / Gemini / Claude) |
| Infra      | Docker, Docker Compose, GitHub Actions, Nginx |

## License

See [`LICENSE`](LICENSE).
