// Data + UI context for the dashboard. Scenario / theme / density live in
// URL search params via TanStack Router, so deep links carry settings.
import React, { createContext, useContext, useMemo } from "react";
// @ts-expect-error jsx module without types
import { THEME_PRESETS, DENSITY_PRESETS, useScaleData } from "./data-utils.jsx";
// @ts-expect-error jsx module without types
import { buildAurTheme } from "./atoms.jsx";

export type ScenarioId = "healthy" | "current" | "crisis";
export type ThemeId = "teal" | "violet" | "rose" | "sky" | "amber";
export type DensityId = "compact" | "cozy" | "spacious";

type DashCtx = {
  scenario: ScenarioId;
  theme: ThemeId;
  density: DensityId;
  themePreset: typeof THEME_PRESETS[keyof typeof THEME_PRESETS];
  densityPreset: typeof DENSITY_PRESETS[keyof typeof DENSITY_PRESETS];
  AUR: ReturnType<typeof buildAurTheme>;
  data: any;
  loading: boolean;
  err: string | null;
};

const Ctx = createContext<DashCtx | null>(null);

export function DashProvider({
  scenario, theme, density, children,
}: {
  scenario: ScenarioId; theme: ThemeId; density: DensityId; children: React.ReactNode;
}) {
  const { data, err, loading } = useScaleData(scenario);
  const themePreset = THEME_PRESETS[theme] || THEME_PRESETS.teal;
  const densityPreset = DENSITY_PRESETS[density] || DENSITY_PRESETS.cozy;
  const AUR = useMemo(() => buildAurTheme(themePreset), [themePreset]);
  const value: DashCtx = { scenario, theme, density, themePreset, densityPreset, AUR, data, loading, err };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useDash(): DashCtx {
  const v = useContext(Ctx);
  if (!v) throw new Error("useDash must be used inside DashProvider");
  return v;
}
