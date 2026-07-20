import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { HealthStatusCard } from "@/features/health/components/health-status-card";
import { useHealthCheck } from "@/features/health/hooks/use-health";

// Mock the hook, not fetch — the component's job is to render given
// states, not to know how the data arrived. Data-fetching behavior is
// covered separately in api-client.test.ts.
vi.mock("@/features/health/hooks/use-health");

const mockedUseHealthCheck = vi.mocked(useHealthCheck);

describe("HealthStatusCard", () => {
  it("shows a loading state while pending", () => {
    mockedUseHealthCheck.mockReturnValue({
      isPending: true,
      isError: false,
      data: undefined,
      error: null,
    } as ReturnType<typeof useHealthCheck>);

    render(<HealthStatusCard />);

    expect(screen.getByText(/checking connection/i)).toBeInTheDocument();
  });

  it("shows health data once loaded", () => {
    mockedUseHealthCheck.mockReturnValue({
      isPending: false,
      isError: false,
      data: { status: "ok", app_name: "InterviewOS", environment: "development" },
      error: null,
    } as ReturnType<typeof useHealthCheck>);

    render(<HealthStatusCard />);

    expect(screen.getByText("ok")).toBeInTheDocument();
    expect(screen.getByText("InterviewOS")).toBeInTheDocument();
  });

  it("shows an error message on failure", () => {
    mockedUseHealthCheck.mockReturnValue({
      isPending: false,
      isError: true,
      data: undefined,
      error: new Error("Network error"),
    } as ReturnType<typeof useHealthCheck>);

    render(<HealthStatusCard />);

    expect(screen.getByText(/could not reach the api/i)).toBeInTheDocument();
  });
});
