import { ThemeToggle } from "@/components/theme-toggle";
import { HealthStatusCard } from "@/features/health/components/health-status-card";

// Server component: no "use client" here. Only the pieces that need
// browser APIs or hooks (ThemeToggle, HealthStatusCard) are client
// components, imported into this server-rendered shell.
export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center gap-8 p-8">
      <div className="flex w-full max-w-md items-center justify-between">
        <h1 className="text-2xl font-semibold">InterviewOS</h1>
        <ThemeToggle />
      </div>

      <p className="max-w-md text-center text-muted-foreground">
        AI-powered interview preparation and simulation platform. This page is
        placeholder scaffolding from Phase 3 — the real dashboard lands in
        Phase 16.
      </p>

      <HealthStatusCard />
    </main>
  );
}
