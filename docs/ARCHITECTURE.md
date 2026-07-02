# Architecture

The one canonical description of how the Scale Ops Command Center works.
Everything else under `docs/archive/` is historical execution material kept for
provenance; when they disagree, this document wins.

## The arc: CSV → Python pipeline → JSON payload → React → static deploy

```
data/*.csv ──▶ src/ scoring engine ──▶ web/public/data/data-{scenario}.json ──▶ React SPA ──▶ Render static site
(synthetic)    (pure pandas, tested)    (one payload per scenario, committed)     (web/)        (render.yaml)
```

1. **Generate** — `src/generate_data.py` emits seeded synthetic CSVs into
   `data/` for one of three scenarios (`healthy` / `current` / `crisis`). The
   seed makes every scenario independently reproducible.
2. **Score** — the `src/` engine (`metrics`, `rules`, `escalation_patterns`,
   `escalation_semantic_clusters`, `workforce_quality`, `capacity_forecast`,
   plus the deterministic briefing generators) turns raw rows into KPIs, risk
   scores, recurrence patterns, and forecasts. These modules accept DataFrames
   and return scored results — no I/O, no framework coupling — and are guarded
   by the pytest suite in `tests/`.
3. **Emit** — `src/build_frontend_data.py` assembles one JSON payload per
   scenario into `web/public/data/`. `src/pipeline.py` orchestrates
   generate → score → emit and validates every payload against a required-keys
   manifest. `scripts/rebuild.sh` is the one-command wrapper.
4. **Render** — the React app (`web/`, TanStack Start in SPA mode, built with
   Vite) fetches `/data/data-{scenario}.json` client-side via a single hook
   (`useScaleData` in `web/src/dashboards/data-utils.jsx`). There is no
   server-side data load.
5. **Deploy** — `render.yaml` defines one static service: `bun install && bun
   run build`, publish `web/dist/client`, with a SPA fallback rewrite so deep
   links resolve. The payloads are committed, so the static build just bundles
   them.

## Single source of truth

Every number on every surface comes from the same committed payload, produced
by the same Python engine. The frontend does **no scoring** — it formats and
navigates. When a figure needs to change, the change lands in `src/`, the
pipeline re-emits the JSON, and every module (and the workbench, and the
exports) moves together. There is nothing to reconcile because there is only
one producer.

## The `{section, focus}` IA model

Navigation state is a pair: **section** (which module — `/health`,
`/patterns`, `/clusters`, `/workforce`, `/capacity`, `/workbench`) and
**focus** (what you are drilled into — `workType`, `teamId`, `contributorId`,
`patternId`, `clusterId`). Focus lives in URL search params, validated by the
`_dash` layout route, alongside the environment params (scenario `s`, theme
`t`, density `d`, vintage `v`). Consequences:

- Deep links carry the full state — refresh mid-drilldown and the view
  survives (the SPA rewrite serves the shell; the router restores the rest).
- Cross-module "follow the thread" links are just `navigate({ to: section,
  search: focus })` — a leadership alert and the drilldown it opens show the
  same number because they share the same payload and the same focus.

## Decision surface vs audit surface

The five dashboards are the **decision surface**: curated views that say what
to do next (Health rollup, Pattern recurrence, Semantic clusters, Workforce
quality, Capacity/SLA forecast). The **Analyst Workbench**
(`web/src/routes/_dash.workbench.tsx`) is the **audit surface**: the same
payload exposed as raw sortable/filterable tables (teams, escalations,
patterns, clusters, contributors, work-type rollup) with client-side CSV/JSON
export of the filtered rows. One payload, one source — an analyst can verify
any dashboard figure against the raw collection behind it without leaving the
app.

## Production path

The prototype's synthetic `generate_data.py` step is what gets replaced in
production; everything downstream of "DataFrames" already runs today.

```
Source Systems              Scheduled Pipeline            Presentation
┌───────────────┐    ┌──────────────────────────┐    ┌───────────────┐
│ Labeling plat │    │ Airflow / cron / Lambda   │    │ Command       │
│ QA system     │───▶│  1. Extract → DataFrames  │───▶│ Center SPA    │
│ Ticketing     │    │  2. src/ scoring engine   │    │ + Workbench   │
│ CSAT surveys  │    │  3. Emit JSON / write DB  │    └───────────────┘
│ Workforce DB  │    │  4. Validate + alert      │
└───────────────┘    └──────────────────────────┘
```

- **Stays:** all `src/` scoring modules. They take DataFrames in and return
  scored results out; the test suite locks the scoring contract regardless of
  where the data comes from.
- **Changes:** the data-source adapter (CSV → SQL/warehouse/API), scheduling
  (manual CLI → cron/Airflow/Lambda), storage (JSON on disk → database or
  served API), and an auth layer in front of the presentation tier.

### Scaling dimensions

- **Data volume:** swap CSV reads for paginated warehouse queries. The scoring
  functions are already vectorized pandas, so the change is at the I/O edge,
  not in the engine.
- **Multi-region:** run one parameterized pipeline pass per region; production
  points each region at its own payload.
- **Real-time:** the batch pipeline stays for weekly review. Add a lightweight
  websocket listener for live escalation alerts alongside it, without touching
  the batch path.
- **Refresh cadence:** the prototype is on-demand. Production runs on an
  hourly/daily schedule with staleness monitoring — the `generated_at`
  timestamp already in every payload is the hook for the freshness check.

## Deliberately deferred

- **Vintage collapse** (`data-pre-fix.json` / `data-post-fix.json` and the
  sidebar vintage selector) — kept because the pre-fix/post-fix pair is the
  before/after demo asset; collapsing it saves little and destroys the demo.
- **`POST /api/rebuild` live fork** — a server endpoint that re-runs the
  pipeline would require abandoning the free static deploy for a running
  service; the local `scripts/rebuild.sh` + in-app "Refresh data" button
  covers the demo motion.
