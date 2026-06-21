# Adopt the offline UX model

The offline HTML has a fundamentally better architecture: every module is a single page with 3 progressive-disclosure levels (board → work-type → team) switched by a `focus` object, with a breadcrumb at the top, a "follow the thread" strip at the bottom, and all environment controls (scenario/accent/density) tucked into the sidebar so the top of the screen is reserved for the user's *trail of thought*. I'll port that model wholesale onto the current TanStack routes, using search params (`wt`, `tm`, `pid`) for focus state so every level is deep-linkable.

## What changes per page

- **Home (`/`)** — keep the name "Home". Insert a **Leadership Attention** section between the KPI strip and the module gateways, with three deterministically-built alerts (top accelerating pattern, top capacity risk, top quality-risk team). Each alert is clickable and threads into the relevant module's deep level.
- **Health (`/health`)** — three levels:
  - L1 (`/health`) — work-type board (one card per work type with all 6 metric cells).
  - L2 (`/health?wt=X`) — team comparison table for one work type + root-cause mix.
  - L3 (`/health?wt=X&tm=Y`) — single team: recent escalations, root-cause mix, tiles.
  - Each level has Breadcrumb on top, ThreadNav at the bottom into B/C/D.
- **Patterns (`/patterns`)** — list with filters; clicking a row navigates to `/patterns?pid=ID` which shows the pattern detail view with affected-teams chips that route into `/health?wt=…&tm=…`. ThreadNav at the bottom.
- **Clusters (`/clusters`)** — each cluster card gets an "Open full pattern drilldown →" link that navigates to `/patterns?pid=…` plus ThreadNav.
- **Workforce (`/workforce`)** — three levels (overview → work-type → team) instead of one dense table with the team detail glued to the bottom. The team level shows a risk-score breakdown with driver bars and per-contributor coaching cards (deterministic, scenario-aware).
- **Capacity (`/capacity`)** — three levels with a forecast pill (Likely stable / Watchlist / At risk / Recovery needed), a recommended-action panel, capacity-risk drivers, and per-team load. The recommendations actually map to dominant drivers (head gap → "add heads", complexity → "cross-train", utilization → "rebalance").
- **Drilldown (`/drilldown`)** — kept as-is so the sidebar stays at 8 items; it's an alternate cross-cut.
- **About (`/about`)** — no functional change.

## Shell + theming

- Move scenario / accent / density controls out of the top bar into the **sidebar** (compact footer block), so the top of every page is reserved for breadcrumb + page chrome.
- Keep the 8-item nav rail. Active route preserves all search params.
- Top bar shrinks to: Live chip · Region · Week · briefing button.

## Data plumbing

- Extend `data-utils.jsx` with the offline version's richer derivations:
  - `deriveQuality(d)` — per-team driver bars, drift, gold-fail/override/peer/rework, plus a deterministic per-team contributor cohort (seeded by team ID, so flipping the scenario re-shuffles consistently) for the coaching cards.
  - `deriveCapacity(d)` — per-work-type forecast (`Likely stable`/`Watchlist`/`At risk`/`Recovery needed`), driver bars, `headGap`, `action`, plus per-team load distribution.
- Keep the old `deriveWorkforce` export as a thin alias so nothing else breaks during the rewrite.

## Atoms

Add to `atoms.jsx`: `Breadcrumb`, `ThreadNav` + `ThreadCard`, `RiskMeter`, `DriverBars`, `PillRow`, `ForecastPill`, `CoachingCard`. Keep all existing atoms.

## Search params (layout)

`_dash.tsx` validator gains optional `wt`, `tm`, `pid` strings alongside `s/t/d`. All `<Link>`s in the sidebar use `search: (prev) => prev` so theme + scenario survive navigation.

## Files touched

- Modify: `src/dashboards/data-utils.jsx`, `src/dashboards/atoms.jsx`, `src/dashboards/shell.tsx`, `src/routes/_dash.tsx`, `src/routes/_dash.index.tsx`, `src/routes/_dash.health.tsx`, `src/routes/_dash.patterns.tsx`, `src/routes/_dash.clusters.tsx`, `src/routes/_dash.workforce.tsx`, `src/routes/_dash.capacity.tsx`.
- Untouched: `_dash.drilldown.tsx`, `_dash.about.tsx`, `modals.jsx`, `app-context.tsx`.

