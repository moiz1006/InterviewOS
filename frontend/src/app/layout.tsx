import type { Metadata } from "next";
import type { ReactNode } from "react";

import { Providers } from "@/app/providers";

import "./globals.css";

export const metadata: Metadata = {
  title: "InterviewOS",
  description: "AI-powered interview preparation and simulation platform.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    // suppressHydrationWarning is the documented next-themes requirement:
    // the theme class is applied client-side before hydration, so the
    // server-rendered `<html>` attributes intentionally won't match on
    // first paint.
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
