import { QueryClient } from "@tanstack/react-query";

/**
 * One QueryClient factory shared by the app. A factory (not a
 * module-level singleton) matters specifically for the server-rendering
 * case: each request on the server needs its own QueryClient so cached
 * data never leaks between users, while the client keeps a single
 * instance across re-renders (see `app/providers.tsx`).
 */
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Slightly conservative defaults for a data-sensitive app
        // (interview sessions, reports) — prefer an extra refetch over
        // showing stale results silently.
        staleTime: 30_000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  });
}
