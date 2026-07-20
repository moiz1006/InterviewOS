# InterviewOS — Build Roadmap

This document is the single source of truth for build progress. Each phase
is only marked complete once code, tests, and docs for that phase exist and
have been reviewed.

| # | Phase | Status |
|---|-------|--------|
| 1 | Repository Setup | ✅ Complete |
| 2 | Backend Structure | ✅ Complete (this commit) |
| 3 | Frontend Structure | ✅ Complete (this commit) |
| 4 | Database | ⬜ Not started |
| 5 | Authentication | ⬜ Not started |
| 6 | Resume Upload | ⬜ Not started |
| 7 | Resume Parsing | ⬜ Not started |
| 8 | ATS Engine | ⬜ Not started |
| 9 | JD Analyzer | ⬜ Not started |
| 10 | AI Engine (LangGraph foundation, provider router) | ⬜ Not started |
| 11 | Interview Engine (HR / Technical / System Design / Behavioral) | ⬜ Not started |
| 12 | Coding Interview | ⬜ Not started |
| 13 | Voice Interview | ⬜ Not started |
| 14 | Group Discussion Simulator | ⬜ Not started |
| 15 | Reports | ⬜ Not started |
| 16 | Dashboard | ⬜ Not started |
| 17 | Docker | ⬜ Not started |
| 18 | CI/CD | ⬜ Not started |
| 19 | Deployment | ⬜ Not started |

## Rules for every phase

1. Explain the architecture and the "why," not just the "what."
2. Ship production-quality code for that phase only — no scaffolding ahead
   of where we are.
3. Explain how to test/verify it.
4. Stop and wait for confirmation before starting the next phase.

## Architecture Decision Records (ADRs)

Non-trivial structural decisions get a numbered ADR in this folder
(`docs/architecture/ADR-XXXX-title.md`) before implementation. This keeps
"why did we do it this way" answerable months later without archaeology
through commit history.

- `ADR-0001-monorepo-layout.md` — why frontend/backend/ai-engine are
  separate top-level directories instead of a single package (added in
  Phase 1).
- `ADR-0002-backend-package-layout.md` — why backend code lives under
  `backend/app/` rather than flat under `backend/` (added in Phase 2).
- `ADR-0003-frontend-structure.md` — feature-folder conventions,
  server/client component split, and TanStack Query vs. Zustand state
  ownership (added in Phase 3).
