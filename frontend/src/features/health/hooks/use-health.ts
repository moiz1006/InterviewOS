import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { HealthResponse } from "@/types/api";

/**
 * Every feature's server-data access is a `useQuery`/`useMutation` hook
 * like this one — components never call `apiClient` or `fetch` directly.
 * This keeps caching, loading/error states, and refetch behavior
 * consistent, and makes the data-fetching logic testable independent of
 * any component.
 */
export function useHealthCheck() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiClient.get<HealthResponse>("/health"),
    // Cheap, side-effect-free endpoint — fine to poll while this demo
    // card is on screen, so a backend restart is visible without a
    // manual refresh.
    refetchInterval: 15_000,
  });
}
