# ADR-0001: Monorepo with separate `frontend/`, `backend/`, `ai-engine/`

**Status:** Accepted
**Phase:** 1 — Repository Setup

## Context

InterviewOS has three distinct workloads:

- A **Next.js frontend** — request/response, deployed to the edge/CDN.
- A **FastAPI backend** — CRUD, auth, orchestration, request/response with
  strict latency budgets.
- An **AI engine** — LangGraph agent graphs that make long-running,
  potentially expensive, occasionally streaming LLM calls across multiple
  providers.

These three have different deployment cadences, different scaling curves,
and different failure modes. A GD (Group Discussion) simulation session
might hold a WebSocket open for 20+ minutes running five agents; a login
request should resolve in under 200ms. Bundling all of it into one
deployable service would force one scaling policy onto workloads that need
different ones.

## Decision

Keep a single Git repository (monorepo) for coordinated versioning and
atomic cross-cutting changes (e.g., changing an API contract touches
backend + frontend in one PR), but keep **three independently
runnable/deployable top-level codebases**:

```
frontend/    — own package.json, own Dockerfile, deployed independently
backend/     — own pyproject/requirements, own Dockerfile
ai-engine/   — own requirements, imported by backend/ in-process for now
```

`ai-engine/` starts as an **in-process library** imported by `backend/`
(Phase 10 decision), not a separate network service — that's the simplest
thing that could work, and we will not split it into its own deployable
until we have evidence (latency, scaling, or team-ownership pressure) that
warrants it. This ADR will be superseded if that happens.

## Consequences

- Each top-level directory gets its own dependency manifest, own linter
  config, own test runner — no shared `node_modules` or shared Python venv
  across frontend/backend.
- `docs/` and `infrastructure/` are shared/cross-cutting by design.
- CI (Phase 18) will need path-based triggers so a frontend-only change
  doesn't run backend test suites and vice versa.
- If `ai-engine/` later becomes its own service, `backend/` will talk to it
  over an internal API — the service boundary already exists at the code
  level (backend never reaches into ai-engine internals, only its public
  agent interfaces), so that split will not require a rewrite.

## Alternatives considered

- **Single Python package, frontend as a subfolder served by FastAPI** —
  rejected: couples frontend deploys to backend deploys, and Next.js SSR
  doesn't fit well behind a Python process.
- **Three separate repositories (polyrepo)** — rejected for now: at this
  stage, one team is building all three layers together and needs atomic
  commits across API contract changes. Can be split later if team
  ownership diverges.
