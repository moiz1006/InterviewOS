# InterviewOS — Backend

FastAPI service. Clean architecture: routes call `services/`, services call
`repositories/`, `models/`/`db/` are the only layer that knows about
SQLAlchemy. No business logic in `api/` route handlers — see
`../CONTRIBUTING.md`.

As of **Phase 2**, this is a running skeleton with one real endpoint
(`/api/v1/health`). Auth, database models, and every domain feature land in
later phases — see `../docs/architecture/00-roadmap.md`.

## Layout

```
app/
├── main.py              app factory: wires settings, logging, middleware, routers
├── core/
│   ├── config.py          typed Settings (pydantic-settings), env-driven
│   ├── logging.py          structlog configuration (JSON in prod, console in dev)
│   └── exceptions.py        AppException hierarchy — framework-agnostic
├── middleware/
│   ├── request_id.py         request ID + structured access log per request
│   ├── security_headers.py   baseline security headers on every response
│   └── exception_handler.py  maps AppException -> consistent JSON error shape
├── api/v1/
│   ├── router.py              aggregates all v1 endpoint routers
│   └── endpoints/health.py     the one concrete route so far
├── dependencies/            FastAPI DI providers (Depends(...) targets)
├── schemas/                  Pydantic request/response models
├── services/  repositories/  models/  db/  tasks/  utils/
│   — present as empty, documented packages; filled in starting Phase 4
tests/
├── conftest.py             TestClient fixture built from the app factory
└── test_health.py           health check, request-id header, error shapes
```

## Local setup

Requires Python 3.11+.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Run it

```bash
cp ../.env.example ../.env       # or backend/.env — either is picked up
uvicorn app.main:app --reload --port 8000
```

Then:

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok","app_name":"InterviewOS","environment":"development"}
```

Interactive API docs: http://localhost:8000/docs

## Test it

```bash
pytest -v
```

Expected: 6 tests pass, covering the health response body, the
`X-Request-ID` header (both generated and echoed-back cases), the security
headers, the 404 shape, and that the OpenAPI schema builds at all (which
exercises every router/schema wiring end-to-end).

## Lint / format / typecheck

```bash
black app tests
ruff check app tests
mypy app
```

## Design notes

- **Why `app/` instead of the flat `api/`, `services/`, ... layout the
  original spec sketched at the repo root?** Python needs an importable
  package root; nesting everything under `backend/app/` keeps
  `backend/pyproject.toml`, `requirements*.txt`, and `tests/` at the
  project root where tooling (pytest, mypy, Docker `COPY`) expects them,
  while `app/` itself remains a clean, single import root (`from app.core
  import ...`). Full rationale documented in
  `../docs/architecture/ADR-0002-backend-package-layout.md`.
- **Why structlog instead of stdlib logging directly?** Structured
  (key=value / JSON) logs are queryable in any log aggregator without
  regex parsing, and `contextvars` binding means a `request_id` bound once
  in middleware automatically shows up on every log line for that request
  — including ones emitted deep inside a service — without threading it
  through every function signature.
- **Why a custom `AppException` hierarchy instead of raising
  `HTTPException` directly from services?** `HTTPException` is a FastAPI/
  Starlette concept. Keeping `services/` and `repositories/` free of web
  framework imports means that logic is reusable from a Celery task or a
  script, not just from an HTTP request — and the exception -> status code
  mapping lives in exactly one place (`middleware/exception_handler.py`)
  instead of being decided ad hoc at every raise site.
