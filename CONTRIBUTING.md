# Contributing to InterviewOS

## Phase-based development

This project is built in the 19 phases listed in
[`docs/architecture/00-roadmap.md`](docs/architecture/00-roadmap.md). Each
phase lands as one or more PRs scoped to that phase only — please don't mix
work from a later phase into an earlier phase's PR, even if it's tempting
("while I'm in here...").

## Branching

- `main` — always deployable.
- `phase/<n>-<short-name>` — work for a given phase, e.g. `phase/5-auth`.
- `fix/<short-description>` — bugfixes against `main`.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/):

```
feat(backend): add refresh token rotation
fix(frontend): correct resume upload progress bar
docs(architecture): add ADR-0004 provider router
chore(infra): bump postgres to 16
```

## Before opening a PR

- [ ] Code is typed (Python: full type hints + mypy clean; TS: no `any`
      without a comment explaining why).
- [ ] No business logic in route handlers — it belongs in `services/`.
- [ ] New env vars are documented in `.env.example`.
- [ ] New structural decisions have an ADR in `docs/architecture/`.
- [ ] Tests added/updated and passing.
- [ ] Roadmap table in `docs/architecture/00-roadmap.md` updated if a phase
      is completed.

## Code style

- Backend: `black`, `ruff`, `mypy` (configured in Phase 2).
- Frontend: `eslint`, `prettier` (configured in Phase 3).
- Every file gets a short header comment explaining its responsibility.
- Files stay under ~300 lines; if a file is growing past that, it's a sign
  it's doing too much — split it.
