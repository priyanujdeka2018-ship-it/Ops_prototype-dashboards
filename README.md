# Scale Regional Ops Command Center

An operations command center for a Scale AI regional-lead style role: a Python
scoring pipeline turns raw ops data (escalations, quality events, SLA, CSAT,
workforce) into one JSON payload per scenario, and a React SPA renders it as
five decision dashboards plus an analyst audit workbench. Deployed as a static
site — no running server.

Full design rationale: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

## Repo map

| Path | What it is |
|---|---|
| `data/` | Synthetic CSVs emitted by the pipeline (regenerated, not hand-edited) |
| `src/` | Python engine: data generation, metric/risk scoring, pattern detection, forecasting, payload builder (`build_frontend_data.py`), orchestrator (`pipeline.py`) |
| `tests/` | Pytest suite guarding the scoring contract (`python -m pytest -q`) |
| `scripts/rebuild.sh` | One-command pipeline rebuild → writes `web/public/data/` |
| `web/` | React app (TanStack Start SPA, Vite, bun) — dashboards + workbench |
| `web/public/data/` | Committed JSON payloads, one per scenario/vintage |
| `render.yaml` | Render static-site deploy (build from `web/`, SPA fallback rewrite) |
| `docs/` | `ARCHITECTURE.md` (canonical) + `archive/` (historical execution docs) |

## Run the pipeline

```bash
pip install -r requirements.txt
./scripts/rebuild.sh              # current scenario (default)
./scripts/rebuild.sh crisis       # or: healthy | current | crisis
python -m src.pipeline --all-scenarios   # regenerate every scenario payload
```

The pipeline generates seeded CSVs into `data/`, scores them with the `src/`
engine, and writes validated JSON payloads into `web/public/data/`. In the
running app, click **Refresh data** to re-pull the JSON without a reload.

## Run the web app

```bash
cd web
bun install
bun run dev        # local dev server
bun run build      # production build → web/dist/client
```

The app fetches `/data/data-{scenario}.json` client-side; the scenario,
theme, density, and drill-down focus all live in URL search params, so any
view is a shareable deep link.

**Deploy:** push to the branch Render watches — `render.yaml` builds `web/`
and publishes `web/dist/client` as a static site with a SPA fallback rewrite.

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

The suite covers the scoring engine and the payload builder — the frontend
does no scoring, so testing the Python contract locks the numbers everywhere.

## Surfaces

- **Dashboards (decision surface):** Health, Patterns, Clusters, Workforce,
  Capacity — curated views that say what to do next.
- **Workbench (audit surface):** `/workbench` — the same payload as raw
  sortable/filterable tables with CSV/JSON export of the filtered rows, so any
  dashboard figure can be verified against its source collection.
