// Pathless layout that wraps every dashboard page in DashProvider + AppShell.
// Global search params (scenario/theme/density) AND focus params (wt/tm/pid)
// live here so they survive every navigation across modules.
import { createFileRoute, Outlet } from "@tanstack/react-router";
import { zodValidator, fallback } from "@tanstack/zod-adapter";
import { z } from "zod";
import { DashProvider } from "@/dashboards/app-context";
import { AppShell } from "@/dashboards/shell";

const searchSchema = z.object({
  s: fallback(z.enum(["healthy", "current", "crisis"]), "current").default("current"),
  t: fallback(z.enum(["teal", "violet", "rose", "sky", "amber"]), "teal").default("teal"),
  d: fallback(z.enum(["compact", "cozy", "spacious"]), "cozy").default("cozy"),
  // vintage — pre-baked snapshot selector (parallel to scenario); "live" uses the scenario
  v: fallback(z.enum(["live", "pre-fix", "post-fix"]), "live").default("live"),
  // focus params (Focus shape, brief §5) — optional, persist across sections
  workType:      fallback(z.string().optional(), undefined as any).default(undefined as any),
  teamId:        fallback(z.string().optional(), undefined as any).default(undefined as any),
  contributorId: fallback(z.string().optional(), undefined as any).default(undefined as any),
  patternId:     fallback(z.string().optional(), undefined as any).default(undefined as any),
  clusterId:     fallback(z.string().optional(), undefined as any).default(undefined as any),
  // patterns filters
  status: fallback(z.string().optional(), undefined as any).default(undefined as any),
  risk:   fallback(z.string().optional(), undefined as any).default(undefined as any),
  who:    fallback(z.string().optional(), undefined as any).default(undefined as any),
});

export const Route = createFileRoute("/_dash")({
  validateSearch: zodValidator(searchSchema),
  component: DashLayout,
});

function DashLayout() {
  const { s, t, d, v } = Route.useSearch();
  return (
    <DashProvider scenario={s} theme={t} density={d} vintage={v === "live" ? undefined : v}>
      <AppShell>
        <Outlet />
      </AppShell>
    </DashProvider>
  );
}
