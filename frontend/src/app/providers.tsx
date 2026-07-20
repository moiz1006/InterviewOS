"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { useState } from "react";

import { createQueryClient } from "@/lib/query-client";

/**
 * All client-only context providers live here, in one file, so
 * `app/layout.tsx` itself can stay a server component. Anything that
 * needs browser APIs or React context (query cache, theme) is a client
 * boundary — everything else in the tree renders on the server by
 * default.
 */
export function Providers({ children }: { children: React.ReactNode }) {
  // `useState(() => ...)` (not a module-level `new QueryClient()`) so each
  // component instance gets its own client — required for React 19/Next
  // App Router where a module-level singleton would leak cached query
  // data across users' server-rendered requests.
  const [queryClient] = useState(createQueryClient);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
}
