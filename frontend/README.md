# InterviewOS — Frontend

Next.js (App Router) + TypeScript. Feature-based structure — see
[`src/features/README.md`](src/features/README.md) for the convention, and
[`../docs/architecture/ADR-0003-frontend-structure.md`](../docs/architecture/ADR-0003-frontend-structure.md)
for the reasoning behind the server/client split and state ownership rules.

As of **Phase 3**, this renders one page that proves the frontend can talk
to the backend built in Phase 2 (a live health-check card), plus dark mode.
Every real feature (auth, resume upload, dashboard, interview rounds, ...)
lands in later phases per
[`../docs/architecture/00-roadmap.md`](../docs/architecture/00-roadmap.md).

## Layout

```
src/
├── app/
│   ├── layout.tsx        root layout — SERVER component
│   ├── page.tsx            home page — SERVER component
│   ├── providers.tsx        QueryClientProvider + ThemeProvider — the one client boundary at the root
│   └── globals.css           Tailwind + shadcn CSS-variable theme (light/dark)
├── components/
│   ├── ui/                    hand-authored shadcn primitives (button, card)
│   └── theme-toggle.tsx        dark mode switch
├── features/
│   ├── README.md                the feature-folder convention
│   └── health/                   reference feature: hooks/ + components/ calling GET /api/v1/health
├── lib/
│   ├── api-client.ts               typed fetch wrapper, throws ApiError matching the backend's error envelope
│   ├── query-client.ts              TanStack QueryClient factory
│   └── utils.ts                      cn() classname helper
├── stores/
│   └── ui-store.ts                    Zustand pattern reference — UI-only state, not server data
└── types/
    └── api.ts                          types mirroring backend Pydantic schemas
```

## Local setup

Requires Node 20+.

```bash
cd frontend
npm install
cp ../.env.example .env.local     # only NEXT_PUBLIC_API_BASE_URL matters here
```

## Run it

Backend must be running first (see `../backend/README.md`):

```bash
npm run dev
```

Open http://localhost:3000 — you should see the InterviewOS home page with
a "Backend connection" card showing `status: ok` (pulled live from
`GET /api/v1/health`) and a working dark-mode toggle. If the backend isn't
running, the card shows a connection error instead of crashing the page —
that's the `isError` branch in `health-status-card.tsx`, exercised
deliberately as part of the loading/error/success contract every feature
follows.

## Test it

```bash
npm run test        # vitest: utils, api-client error handling, HealthStatusCard states
npm run typecheck   # tsc --noEmit
npm run lint
```

## ⚠️ Not yet verified by actually running

This was built in a sandboxed environment with no access to the npm
registry, so `npm install` / `npm run dev` / `npm run build` /
`npm run test` have **not** been executed here — only hand-review and,
where possible, static checks (see below). Please run the commands above
for real before treating this as done; if anything fails to install or
build, tell me the error and I'll fix it before Phase 4.

What I verified without network access:
- Every `package.json`, `tsconfig.json`, `.prettierrc.json`, and
  `components.json` is valid JSON.
- Import paths and the `@/*` alias are consistent across every file by
  hand-trace (`tsconfig.json` `paths` ↔ `vitest.config.ts` `resolve.alias`
  ↔ actual `@/...` imports).
- The API error shape in `lib/api-client.ts` matches the backend's actual
  envelope from `backend/app/middleware/exception_handler.py` field for
  field (`error.code`, `error.message`, `error.details`).
