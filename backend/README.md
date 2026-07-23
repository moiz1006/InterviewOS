# InterviewOS — Backend

FastAPI service. Clean architecture: routes call `services/`, services call
`repositories/`, `models/`/`db/` are the only layer that knows about
SQLAlchemy. No business logic in `api/` route handlers — see
`../CONTRIBUTING.md`.

As of **Phase 4**, the full database schema exists (12 tables, all
relationships, an initial Alembic migration) alongside the Phase 2
skeleton and the `/health/ready` DB connectivity check. Auth and every
domain feature still land in later phases — see
`../docs/architecture/00-roadmap.md`.

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
│   └── endpoints/health.py     GET /health (liveness) + GET /health/ready (DB check)
├── dependencies/            FastAPI DI providers (Depends(...) targets)
│   └── db.py                  DbSessionDep — see app/db/session.py
├── schemas/                  Pydantic request/response models
├── db/
│   ├── base.py                 declarative Base + constraint naming convention
│   └── session.py               async engine, session factory, get_db_session
├── models/                    12 SQLAlchemy models — one file per table (Phase 4)
│   ├── mixins.py                UUIDPrimaryKeyMixin, TimestampMixin
│   └── enums.py                  ResumeStatus, RoundType, etc.
├── repositories/
│   └── base.py                  generic BaseRepository[ModelType] — domain repos subclass this from Phase 5
├── services/  tasks/  utils/
│   — present as empty, documented packages; filled in starting Phase 5
alembic/
├── env.py                     async-aware, reads DATABASE_URL from Settings
└── versions/0001_initial_schema.py   hand-written initial migration (see Database section below)
tests/
├── conftest.py             app + client fixtures (app exposed for dependency_overrides)
├── test_health.py            health check, request-id header, error shapes
└── test_health_ready.py       readiness check with a fake DB session override
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

## Database (Phase 4)

Requires a local Postgres 16+ instance. Quickest way without Docker
(Docker Compose lands in Phase 17):

```bash
# macOS (Homebrew) example — adjust for your platform
brew install postgresql@16
brew services start postgresql@16
createuser interviewos -P        # password: changeme (or whatever you set in .env)
createdb interviewos -O interviewos
```

Then, with `DATABASE_URL` in `.env` pointing at it (see `.env.example`):

```bash
alembic upgrade head
```

Verify:

```bash
psql -U interviewos -d interviewos -c '\dt'     # should list all 12 tables
curl http://localhost:8000/api/v1/health/ready   # {"status":"ready","database":"connected"}
```

Schema reference: [`../docs/architecture/erd.md`](../docs/architecture/erd.md)
(Mermaid ER diagram) and
[`../docs/architecture/ADR-0004-database-schema.md`](../docs/architecture/ADR-0004-database-schema.md)
(why JSONB vs. columns, enum choices, FK ondelete rules).

**⚠️ Not yet verified by actually running.** No network access in the
sandbox this was built in means `alembic upgrade head` has not been run
against a real Postgres instance. The migration was hand-checked
column-by-column against every model (see ADR-0004's last section) but
that's not a substitute for actually running it. Please run the commands
above for real and tell me if anything breaks.

### Adding a new migration later

```bash
# after changing a model in app/models/
alembic revision --autogenerate -m "add xyz column"
# ALWAYS read the generated migration before committing it — autogenerate
# misses some changes (renamed columns, some constraint changes) and
# occasionally proposes reasonable-looking but wrong diffs.
alembic upgrade head
```

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
