import { create } from "zustand";

/**
 * Zustand is for client-only UI state that doesn't belong in the server
 * cache — sidebar open/closed, wizard step, in-progress form UI state that
 * isn't persisted yet. Server data (resumes, interview sessions, reports)
 * belongs in TanStack Query (`lib/query-client.ts`), not here — don't
 * duplicate server state into a Zustand store just to avoid a `useQuery`
 * call.
 *
 * This is the first store, kept intentionally small, to establish the
 * pattern. Domain-specific stores (e.g. an in-progress interview session's
 * local state) land in their own `features/<name>/store.ts` starting
 * Phase 11+, following this same shape.
 */
interface UIState {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSidebarOpen: (open) => set({ isSidebarOpen: open }),
}));
