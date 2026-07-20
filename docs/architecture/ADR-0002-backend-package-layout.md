# ADR-0002: `backend/app/` package layout with a `src`-style project root

**Status:** Accepted
**Phase:** 2 — Backend Structure

## Context

The original spec sketches the backend's clean-architecture folders
(`api/`, `services/`, `repositories/`, `models/`, `schemas/`,
`dependencies/`, `middleware/`, `core/`, `db/`, `utils/`, `tasks/`) as if
they sit directly under `backend/`. Taken literally, that puts Python
import roots, `pyproject.toml`, `requirements.txt`, and `tests/` all in
the same flat directory.

Two problems with that:

1. **Import ambiguity.** Without a single package root, `api/` is a
   top-level import (`import api`) that collides with nothing today but
   will fight for namespace with any third-party package named similarly,
   and makes `from api.v1 import router` vs. `from backend.api.v1 import
   router` depend on *how* the process was launched (cwd-relative imports
   are a classic source of "works on my machine").
2. **Tooling expects a project root separate from the package.** pytest,
   mypy, Docker `COPY app/ ./app/` + `COPY requirements.txt .`, and
   `pip install -e .` all assume a project root (containing
   `pyproject.toml`) with the actual importable code nested one level
   in — not sharing the same directory.

## Decision

```
backend/
├── pyproject.toml        tool config: black, ruff, mypy, pytest
├── requirements.txt
├── requirements-dev.txt
├── app/                    <- the single importable package root
│   ├── main.py
│   ├── core/  api/  services/  repositories/  models/  schemas/
│   ├── dependencies/  middleware/  db/  utils/  tasks/
└── tests/                  mirrors app/ structure, imports `from app...`
```

Every module inside `app/` imports other modules with the full
`from app.core.config import Settings` form — never relative imports
across layers — so it reads the same regardless of where the process is
launched from, as long as `backend/` is on the path (which running
`uvicorn app.main:app` from `backend/`, or a Docker image with `WORKDIR
/backend`, both guarantee).

## Consequences

- One clear import root (`app`) instead of eleven independent top-level
  packages.
- `backend/Dockerfile` (Phase 17) copies `requirements*.txt` and `app/`
  separately, which also gives better Docker layer caching (deps installed
  in a layer that only invalidates when `requirements.txt` changes, not on
  every code edit).
- Costs one level of nesting (`app.core.config` instead of `core.config`)
  — judged a small, permanent, well-understood cost against the
  alternative's ambiguity.

## Alternatives considered

- **Flat layout exactly as sketched in the spec** — rejected for the
  import/tooling reasons above.
- **`src/` layout (`backend/src/interviewos/...`)** — a common Python
  convention, rejected only because `app/` is more idiomatic within the
  FastAPI ecosystem specifically and every FastAPI example/tutorial a
  future contributor will reference uses this shape, reducing onboarding
  friction.
