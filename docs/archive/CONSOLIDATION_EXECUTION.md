# Scale Ops Command Center — Consolidation Execution Spec

> Place this at `docs/CONSOLIDATION_EXECUTION.md` in `Ops_prototype-dashboards`.
> This is the execution brief. Heavy work runs in **Claude Code**, against this doc.
> The architectural decisions are settled — execute, don't re-litigate.

---

## 0. Decision recap (settled)

- **Option A:** one repo, one source of truth = `Ops_prototype-dashboards` (Render-hosted Python).
- **Frontend** = the Lovable TanStack/TS app (`ops-dashboards/src`), pulled in as canonical UI.
- **Scoring** = Module C/D move into Python; every frontend *reads* scores, never computes them.
- **Aurora (`Scale.zip`/`.patch`/`.bundle`) code is retired** — but its **information architecture is ported** (the `{section, focus}` nav model + Breadcrumb/ThreadNav). We keep D's engineering, adopt C's IA.

---

## 1. Target repo layout (after merge)

```
Ops_prototype-dashboards/
├── app.py, pages/            # Streamlit analyst workbench (kept — see Phase 6)
├── src/                      # Python pipeline + scoring (single source of truth)
│   ├── pipeline.py           # orchestrator CLI
│   ├── generate_data.py      # SCENARIO_MULTIPLIERS, RANDOM_SEED=42
│   ├── build_frontend_data.py# EMITS the full payload (Phase 3 widens this)
│   ├── workforce_quality.py  # Module C engine
│   ├── capacity_forecast.py  # Module D engine
│   └── data_loader.py
├── tests/                    # pytest (currently 83; grows in Phase 3)
├── web/                      # ← TanStack app lands here (replaces old frontend/)
│   ├── src/ …                # ported from ops-dashboards/src
│   └── public/data/*.json    # ← pipeline writes here (the deploy artifact)
├── scripts/rebuild.sh        # ← Phase 5: one-command pipeline rebuild
├── render.yaml               # ← Phase 2 rewrites this
└── docs/
```

**Decision:** the TanStack app lives in `web/` (clean name, no legacy baggage). Delete the old
`frontend/` (the single-file Aurora). The pipeline's JSON output path changes from `frontend/data/`
to `web/public/data/`. *Alternative: reuse `frontend/`; rejected to avoid confusing old vs new.*

---

## 2. Phase plan

| # | Phase | Owner | Definition of done |
|---|---|---|---|
| 1 | Land the backend | **You** (GitHub) | PR `claude/loving-shannon-3ax3td` → `main` merged; 83 tests green; `data/*.csv` untracked |
| 2 | Port TanStack + Render serving | Claude Code + **you** (Render) | App builds & deploys; existing UI + JS scoring intact |
| 3 | Python emit (the contract) | Claude Code | Payload carries C/D + leadership; JS scoring deleted; routes read scores; tests grow |
| 4 | IA redesign | Claude Code | `{section, focus}` nav, Breadcrumb + ThreadNav, Leadership Attention, per-section drill; `drilldown` route retired |
| 5 | Live data-refresh | Claude Code | Refresh button + freshness stamp + rebuild script + vintages |
| 6 | Streamlit fate | — | Kept as analyst workbench; retirement deferred |

Sequence rationale: **3 before 4** so the IA reads the final payload; **5 rides with 4** (both touch the shell/hook). Each phase is one reviewable PR.

---

## 3. Phase detail

### Phase 1 — Land the backend *(you, on GitHub)*
1. Confirm `pytest -q` → 83 passing on the branch.
2. Open PR `claude/loving-shannon-3ax3td` → `main`; merge.
3. `git rm --cached data/*.csv && git commit` (regenerable from `RANDOM_SEED=42`; already in `.gitignore`).
- *Why first:* lands the tested pipeline as the foundation before any porting. Zero new code.

### Phase 2 — Port the TanStack app + Render serving *(Claude Code; you set Render)*
1. Copy `ops-dashboards/src`, `public/`, config (`vite.config.ts`, `package.json`, `tsconfig`, etc.) into `web/`. Delete old `frontend/`.
2. Point the pipeline's output at `web/public/data/` (edit the write path in `build_frontend_data.py` / `pipeline.py`).
3. **Serving model — recommended: static.** The app fetches data client-side from `public/data/*.json`; there is no server-side data load, so SSR buys nothing. Configure the build for a static/SPA output and serve `web/dist` as a **Render Static Site** (free).
   - The Lovable `vite.config.ts` uses `@lovable.dev/vite-tanstack-config`, whose Nitro target defaults to **Cloudflare** — change the preset to a static/prerender output (or SPA fallback). **Spike this first**; it's the only build-config unknown.
   - *Alternative:* Node web service (Nitro `node-server` preset, Render runs the built server entry). Use only if static prerender fights back or you later want true SSR.
4. Rewrite `render.yaml`: replace `scale-ops-aurora` (the `python -m http.server` static service) with the built-output static site. Keep the Streamlit service for now (Phase 6).
- *Why isolate this:* keeping the schema change (Phase 3) out of the deploy reconfig means a broken deploy has one obvious cause.

### Phase 3 — Python emit: the data contract *(Claude Code)* — highest value
1. In `build_frontend_data.py`, **import the engines** (`workforce_quality`, `capacity_forecast`) and add builders that emit the `workforce`, `capacity`, and `leadership` blocks (schema in §4).
2. The recommended-action **thresholds** move into Python too (they're scoring semantics) — emit `action`, `decision`, `headGap` for capacity; `action`, `drivers`, `quality_gap` for workforce.
3. Extend the test suite: assert the new payload keys exist and that emitted scores equal the engines' outputs for a fixed seed. (`tests/` grows past 83.)
4. Regenerate all scenario JSONs.
5. In `web/src/dashboards/data-utils.jsx`, **delete `deriveWorkforce`, `deriveCapacity`, `deriveQuality`**; the workforce/capacity/overview routes now read `data.workforce` / `data.capacity` / `data.leadership`.
- *Result:* one scoring implementation, one test suite — exec and analyst views show identical numbers.

### Phase 4 — IA redesign *(Claude Code)* — see §5
### Phase 5 — Live data-refresh *(Claude Code)* — see §6

### Phase 6 — Streamlit fate
Keep the Streamlit pages as the analyst workbench; the engine + tests stay regardless, so the pages cost nothing. Revisit retirement once the TanStack app fully covers all five modules.

---

## 4. The payload contract (load-bearing)

`build_frontend_data.build_payload()` emits this shape; the frontend reads it and never derives.
Express the same shape as the frontend's TypeScript data types.

```ts
interface Payload {
  // — meta (already emitted; SURFACE in the UI, Phase 5) —
  generated_at: string;          // ISO8601
  scenario: string;              // "current" | "healthy" | "crisis" | vintage label
  pipeline_version: string;
  row_counts: Record<string, number>;
  region: string; weekStart: string; refDate: string;

  // — A · Health (exists today) —
  kpis: { sla_adherence:number; csat_7d:number; backlog:number;
          aged_backlog_72h:number; avg_quality:number };
  kpiTrends: { sla:number[]; csat:number[]; backlog:number[]; quality:number[] };
  totals: { escalations:number; open:number; sev1:number };
  weeklyTrend: { week:string; count:number }[];
  workTypeRollup: { work_type:string; sla:number; csat:number; quality:number;
                    sev1:number; volume:number }[];
  teams: { team_id:string; name:string; work_type:string;
           sla:number; csat:number; quality:number; escalations:number }[];

  // — B · Patterns + Clusters (ensure clusters emitted for B2) —
  patterns: { pattern_id:string; risk_level:"High"|"Medium"|"Low";
              recurrence_status:string; /* … */ }[];
  clusters: { cluster_id:string; theme:string; members:number; /* … */ }[];

  // — C · Workforce Quality — NEW, from src/workforce_quality.py —
  workforce: {
    region: { highRiskTeams:number; avgQuality:number };
    byWorkType: { work_type:string; riskLevel:string; avgQuality:number;
                  teamsAtRisk:number }[];
    teams: { team_id:string; name:string; work_type:string;
             risk_score:number; risk_band:string; drivers:string[];
             action:string; quality_gap:number }[];
    contributors: { contributor_id:string; team_id:string;
                    risk_score:number; risk_band:string;
                    drivers:string[]; coaching:string }[];
  };

  // — D · Capacity & SLA — NEW, from src/capacity_forecast.py —
  capacity: {
    region: { atRisk:number; agedShare:number; forecast:string };
    byWorkType: { work_type:string; forecast:string; riskLevel:string;
                  complexity:number; action:string; headGap:number;
                  decision:string }[];
    teams: { team_id:string; name:string; work_type:string;
             utilization:number; load:number; action:string }[];
  };

  // — Overview · Leadership attention — NEW, derived from top-ranked signals —
  leadership: {
    headline: string;                       // scenario-aware sentence
    alerts: {                               // ≤ 3
      kind: "pattern" | "capacity" | "quality";
      title: string; body: string;
      target: { section: string; focus: Record<string,string> };  // click-through
    }[];
  };
}
```

`leadership.alerts` = top escalation pattern → `{section:"patterns", focus:{patternId}}`, top
capacity risk → `{section:"capacity", focus:{workType}}`, top quality risk →
`{section:"quality", focus:{teamId}}` (mirrors Aurora's `buildAlerts`).

---

## 5. Frontend nav model + primitives (Phase 4)

**One focus shape; only the relevant keys are set per section:**
```ts
type Focus = {
  workType?: string; teamId?: string; contributorId?: string;
  patternId?: string; clusterId?: string;
};
```

- **Drill = typed search params**, not a separate route. Each section route declares
  `validateSearch` over `Focus`, so `/capacity?workType=labeling&teamId=T03` deep-links a level
  and survives refresh. *(This improves on Aurora, whose drill was in-memory `useState`.)*
- **`go(section, focus)`** = `navigate({ to: '/'+section, search: focus })`.
- **`Breadcrumb({ items })`** — `items: { label:string; to?:string; search?:Focus }[]`; earlier
  items clickable, last accented. Renders the trail at top.
- **`ThreadNav({ items, label = "Follow the thread" })`** — `items: { kicker:string; title:string;
  hint:string; to:string; search?:Focus }[]`; up-to-3 gateway cards at the bottom, including
  **cross-module** jumps.
- **Per-section render rule:** `contributorId || teamId → team/contributor level; workType →
  work-type level; else → region level.` Apply to Health, Patterns, Clusters, Workforce, Capacity.
- **Leadership Attention** block on Home: render `data.leadership.headline` + `.alerts`, each alert
  calling `go(target.section, target.focus)`.
- **Capacity/Workforce detail:** render the `action` + `decision` panels from the payload (the
  "Recommended action / Decision" framing), plus a `ThreadNav` to the sibling modules for that
  work-type/team.
- **Retire `web/src/routes/_dash.drilldown.tsx`** — its job is absorbed by per-section focus levels.
- **Sidebar:** keep the 8-button rail; move the **scenario / accent / density** toggles into the
  sidebar footer. Keep them as layout-level search params so they persist across sections.

Build `Breadcrumb` + `ThreadNav` as shared shadcn-styled components under `web/src/components/nav/`.

---

## 6. Live data-refresh capability (Phase 5)

**Recommended path (static-safe): local rebuild + in-app refresh + pre-baked vintages.**

1. **`useScaleData(scenario, vintage?)`** — add `reloadKey` state; effect deps
   `[scenario, vintage, reloadKey]`; return `{ data, err, loading, meta, refresh }` where
   `meta = { generated_at, row_counts, pipeline_version }` and `refresh = () => setReloadKey(k => k+1)`.
   Re-pulls the JSON with no page reload.
2. **`<FreshnessStamp meta={meta} />`** in the shell header — renders "data as of {generated_at} ·
   {Σ row_counts} rows · pipeline {pipeline_version}". This metadata is generated today and thrown
   away; surfacing it makes the update *legible* when you refresh.
3. **`<RefreshButton onClick={refresh}>Refresh data</RefreshButton>`** in the shell.
4. **`scripts/rebuild.sh`** — `python -m src.pipeline --scenario "${1:-current}"` (writes to
   `web/public/data/`). Add a `--label <name>` flag to the pipeline to emit `data-<name>.json` for
   vintages.
5. **Vintages** — commit 1–2 extra snapshots (e.g. `data-week1.json`, `data-week2.json`, or
   `pre-fix`/`post-fix`); add a **vintage selector** in the sidebar (parallel to scenario) that sets
   the fetch label. This is the always-works switcher on the deployed URL.

**Demo motion:** change one legible input (a scenario multiplier, or a one-line escalation-append
script — *don't* hand-edit seven CSVs live) → `./scripts/rebuild.sh` → click **Refresh** → the whole
board moves, identically across every module (the payoff of Phase 3's single source of truth).

### Appendix — optional live-on-URL fork (riskier)
If the rebuild must run **on the deployed URL** in front of the evaluator:
- Add `POST /api/rebuild` (FastAPI) → `build_payload(...)` → returns JSON; frontend posts and sets
  data in state.
- Deploy becomes **static site + a Python API service** (not static-only). Set `VITE_API_BASE`;
  enable CORS for the static origin.
- **Cost:** a running service + a live failure surface mid-demo. Enable only if you want upload/tweak
  on the URL itself; otherwise the recommended path is safer.

---

## 7. What runs where

- **You (GitHub / Render):** open the Phase 1 PR; set the Render service config in Phase 2; flip
  env vars only if you take the optional API fork.
- **Claude Code:** the port, the Python emit + JS deletion, the IA redesign, the refresh wiring, the
  scripts. Reference files by path; don't paste whole files into chat.

---

## 8. Final definition of done (whole merge)

- `pytest -q` green (now > 83: adds C/D-emit + leadership tests).
- **Parity:** Home's leadership alert for team X and the drilled-in view of team X show identical
  numbers — proves the single source of truth.
- **Freshness:** flip a vintage *or* run `rebuild.sh` + Refresh → every module updates consistently
  and the freshness stamp changes.
- **Trail:** Breadcrumb + ThreadNav present on every drilled view; deep-linking
  `/capacity?workType=x&teamId=y` restores that exact level.
- **Clean:** no `deriveWorkforce` / `deriveCapacity` / `deriveQuality` left in the frontend; no
  `_dash.drilldown.tsx`.
