# `features/`

One folder per product feature/domain, not per file type. Each feature
folder owns everything specific to it:

```
features/<name>/
├── components/     feature-specific UI (not reusable elsewhere — if it
│                    becomes reusable, promote it to components/ui/)
├── hooks/            useQuery/useMutation hooks — the ONLY place that
│                      calls apiClient for this feature
├── store.ts           feature-local Zustand store, if the feature needs
│                        client state beyond what the server cache gives it
│                          (optional — most features won't need one)
└── schemas.ts          Zod schemas for this feature's forms, if any
```

Rules:

- **Components never call `apiClient` or `fetch` directly.** All data
  access goes through a hook in `hooks/`. This is what makes loading/error
  states consistent and lets a component be tested by mocking the hook
  instead of mocking `fetch`.
- **No cross-feature imports of internals.** `features/resume/` should
  never `import` something from inside `features/interview/components/`.
  Shared UI belongs in `src/components/`; shared logic belongs in
  `src/lib/`.
- **A feature folder can be deleted cleanly.** If removing
  `features/group-discussion/` requires hunting through unrelated files to
  fully remove it, something leaked out of the folder that shouldn't have.

## Current features

- `health/` — Phase 3 scaffolding proving the frontend ↔ backend wiring
  works end-to-end (calls `GET /api/v1/health`). Temporary; removed once
  Phase 16's dashboard replaces the home page.

Every real product feature (auth, resume upload, ATS score, interviews,
group discussion, reports) gets its own folder here starting from the
phase that introduces it — see `../../../docs/architecture/00-roadmap.md`.
