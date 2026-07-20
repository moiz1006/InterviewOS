"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useHealthCheck } from "@/features/health/hooks/use-health";

/**
 * Proves the frontend/backend wiring end-to-end: this card calls the real
 * `GET /api/v1/health` endpoint built in Phase 2 through the full stack
 * (apiClient -> TanStack Query -> this component), including loading and
 * error states. It's temporary scaffolding, not a permanent feature — it
 * gets removed once the real dashboard (Phase 16) gives users something
 * more useful to look at.
 */
export function HealthStatusCard() {
  const { data, isPending, isError, error } = useHealthCheck();

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Backend connection</CardTitle>
        <CardDescription>Live status of the InterviewOS API</CardDescription>
      </CardHeader>
      <CardContent>
        {isPending && <p className="text-sm text-muted-foreground">Checking connection…</p>}

        {isError && (
          <p className="text-sm text-destructive">
            Could not reach the API: {error instanceof Error ? error.message : "Unknown error"}
          </p>
        )}

        {data && (
          <dl className="grid grid-cols-2 gap-y-1 text-sm">
            <dt className="text-muted-foreground">Status</dt>
            <dd className="font-medium capitalize">{data.status}</dd>
            <dt className="text-muted-foreground">Service</dt>
            <dd className="font-medium">{data.app_name}</dd>
            <dt className="text-muted-foreground">Environment</dt>
            <dd className="font-medium capitalize">{data.environment}</dd>
          </dl>
        )}
      </CardContent>
    </Card>
  );
}
