# ADR-0003: Frontend structure — feature folders, server/client split, state ownership

**Status:** Accepted
**Phase:** 3 — Frontend Structure

## Context

The spec calls for a "feature-based folder structure" and "Server
Components where appropriate," plus TanStack Query, Zustand, React Hook
Form, and Zod all present in the stack. Left unspecified: where the line
is between TanStack Query and Zustand (a common source of duplicated,
drifting state in React apps), and how "feature-based" avoids becoming a
grab-bag once there are a dozen features (resumes, ATS, JD analysis,
interview rounds, group discussion, reports...).

## Decisions

### 1. Server state vs. client state is a hard line, not a preference

- **TanStack Query owns everything that comes from the API** — resumes,
  sessions, reports, scores. It already solves caching, refetching, and
  loading/error states; duplicating that into a Zustand store would create
  two sources of truth that drift.
- **Zustand owns UI-only state that has no server representation** —
  sidebar open/closed, wizard step, in-progress local-only interaction
  state. See `src/stores/ui-store.ts`'s doc comment, which states this
  rule at the point someone is most likely to violate it.

### 2. `features/<name>/` is the unit of ownership, not `components/`,
`hooks/`, `types/` at the top level

A components-first split (`components/`, `hooks/`, `services/` each
containing files for every feature mixed together) scales badly past a
handful of features — finding everything related to "group discussion"
means grep-ing four directories. Instead:

```
src/features/<name>/{components,hooks,store.ts,schemas.ts}
```

Rule enforced by convention (documented in
`src/features/README.md`, not yet lint-enforced): no feature imports
another feature's internals. Only `src/components/`, `src/lib/`,
`src/types/` are shared.

### 3. Components never call `fetch`/`apiClient` directly

Every data access is a `useQuery`/`useMutation` hook in
`features/<name>/hooks/`. `features/health/` is the reference
implementation: `hooks/use-health.ts` owns the query,
`components/health-status-card.tsx` only renders `data`/`isPending`/
`isError`. This is also why the component test
(`health-status-card.test.tsx`) mocks the hook, not `fetch` — the
component's contract is "render these states correctly," not "know how to
fetch."

### 4. Client boundaries are pushed as deep as possible

`app/layout.tsx` and `app/page.tsx` are server components. The only
`"use client"` files are `app/providers.tsx` (holds the QueryClient +
ThemeProvider), `components/theme-toggle.tsx` (reads/writes theme, needs
`useState`/`useEffect`), and `features/health/components/health-status-card.tsx`
(uses the `useHealthCheck` hook). This isn't cosmetic — every server
component ships zero client JS for that subtree, which matters more as
the app grows (an interview report page, for example, should be able to
render mostly on the server).

### 5. Shadcn UI components are hand-authored, not CLI-generated, in this
environment

Normally `npx shadcn@latest add button card` scaffolds these. This build
environment has no network access to npm, so `components/ui/button.tsx`
and `card.tsx` were written by hand, matching shadcn's actual generated
output (same `cva` variant structure, same Tailwind classes, same `cn()`
usage) so that running the real CLI later to add more components (`badge`,
`dialog`, `select`, ...) drops in cleanly alongside them without a style
mismatch.

## Consequences

- Adding a new feature means adding one folder, not touching four
  existing ones.
- `features/health/` will be deleted once Phase 16 ships the real
  dashboard — it's explicitly labeled as temporary scaffolding in its own
  README entry, not left to be mistaken for a real feature later.
- The server/client split means every new page should default to a server
  component and only add `"use client"` where a hook/browser API forces
  it — reviewers should push back on `"use client"` at the top of a page
  file.
