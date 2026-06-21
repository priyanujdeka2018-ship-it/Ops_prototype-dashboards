// {section, focus} navigation for the command center.
// One Focus shape; only the relevant keys are set per section. Focus lives in
// the _dash layout search params (see routes/_dash.tsx) so a drilled level
// deep-links and survives refresh. `go(section, focus)` preserves the env
// (scenario/accent/density) and resets focus to the new target.
import { useNavigate } from "@tanstack/react-router";

export type Focus = {
  workType?: string;
  teamId?: string;
  contributorId?: string;
  patternId?: string;
  clusterId?: string;
};

export const FOCUS_KEYS = [
  "workType",
  "teamId",
  "contributorId",
  "patternId",
  "clusterId",
] as const;

/** Returns go(section, focus): navigate to /section, keeping s/t/d, replacing focus. */
export function useGo() {
  const navigate = useNavigate();
  return (section: string, focus: Focus = {}) =>
    navigate({
      to: ("/" + section) as any,
      search: ((prev: any) => {
        const next: any = { ...prev };
        for (const key of FOCUS_KEYS) delete next[key];
        return { ...next, ...focus };
      }) as any,
    });
}

/** Per-section drill level from the active focus (brief §5 render rule). */
export function focusLevel(focus: Focus): "region" | "work-type" | "team" {
  if (focus.contributorId || focus.teamId) return "team";
  if (focus.workType) return "work-type";
  return "region";
}
