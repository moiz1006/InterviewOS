/**
 * Types mirroring backend Pydantic schemas (`backend/app/schemas/`).
 * Kept hand-written and 1:1 with the backend for now; if drift becomes a
 * problem once there are dozens of these, revisit generating them from
 * the OpenAPI schema at `/api/v1/openapi.json` (tracked as a follow-up,
 * not done preemptively — see CONTRIBUTING.md on avoiding premature
 * tooling).
 */

// Mirrors backend/app/schemas/health.py::HealthResponse
export interface HealthResponse {
  status: string;
  app_name: string;
  environment: string;
}
