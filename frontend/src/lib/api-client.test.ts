import { afterEach, describe, expect, it, vi } from "vitest";

import { apiClient, ApiError } from "@/lib/api-client";

function mockFetchOnce(response: Partial<Response> & { jsonBody?: unknown }) {
  const { jsonBody, ...rest } = response;
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: rest.ok ?? true,
      status: rest.status ?? 200,
      statusText: rest.statusText ?? "OK",
      json: async () => jsonBody,
    })
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("apiClient", () => {
  it("returns parsed JSON on success", async () => {
    mockFetchOnce({ ok: true, status: 200, jsonBody: { status: "ok" } });

    const result = await apiClient.get<{ status: string }>("/health");

    expect(result).toEqual({ status: "ok" });
  });

  it("throws a typed ApiError carrying the backend's error envelope", async () => {
    mockFetchOnce({
      ok: false,
      status: 404,
      jsonBody: { error: { code: "not_found", message: "Resume not found" } },
    });

    await expect(apiClient.get("/resumes/missing")).rejects.toMatchObject({
      status: 404,
      code: "not_found",
      message: "Resume not found",
    } satisfies Partial<ApiError>);
  });
});
