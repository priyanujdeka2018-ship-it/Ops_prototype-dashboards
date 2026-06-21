# Scale Regional Ops Command Center

## Current Status

**Module A MVP complete. Module B MVP added. Module B v2 semantic clustering added. Module C workforce quality scorer added. Module D capacity, staffing, and SLA forecasting added.**

This repository contains an interview-ready Streamlit prototype for a Scale AI Operations / Regional Lead style role.

The command center now includes:

1. **Module A: Regional Operations Health Dashboard**
2. **Module B v1: Escalation Pattern Recurrence Detector**
3. **Module B v2: Semantic Escalation Clustering and Structural Fix Cards**
4. **Module C: Distributed Workforce Quality Scorer**
5. **Module D: Capacity, Staffing, and SLA Forecasting**

## Interview Positioning

> In my first 60 days, I would want a single regional operating view that surfaces SLA, backlog, CSAT, quality, escalation risk, workforce quality risk, and capacity risk before customer impact lands. I built this prototype to show the operating system I would bring to the role.

Module B extends that story:

> Module A tells me where regional health is degrading. Module B tells me whether escalations are isolated incidents or recurring operating-system failures. This helps leadership move from reactive escalation handling to pattern-based prevention.

Module C completes the quality layer:

> I do not want to use quality data as a punitive scoreboard. I want to use it as an operating signal. Module C identifies where quality risk is emerging across teams, cohorts, and work types, then turns that signal into coaching and calibration actions.

Module D completes the capacity layer:

> I do not want staffing decisions to be reactive after SLA misses happen. Module D turns backlog, inflow, throughput, complexity, and contributor availability into an early-warning view so managers can rebalance work, cross-train, or add coverage before customer impact lands.

## Module A: Regional Operations Health Dashboard

Module A gives a regional operations leader one operating view across:

- SLA adherence
- CSAT
- Backlog
- Aged backlog over 72 hours
- Escalation rate
- Quality score
- Rework rate
- First-contact-resolution proxy

Module A includes:

- Executive KPI tiles
- Regional health heatmap
- Work type drilldown
- Team drilldown
- Rule-based anomaly detection
- Weekly ops briefing generator
- Synthetic data only
- Interview demo script
- Final MVP checklist

## Module B v1: Escalation Pattern Recurrence Detector

Module B detects when escalations are not isolated events but recurring patterns.

It answers:

1. Which escalation patterns are repeating?
2. Which work types, teams, customer segments, and root causes are recurring?
3. Which patterns are becoming more severe or more frequent?
4. Which patterns are unresolved or slow to resolve?
5. What should leadership do about repeat escalations?

Module B includes:

- Pattern key builder
- Recurrence scoring
- Pattern status classification
- Pattern risk table
- Pattern drilldown
- Top repeat root-cause charts
- Recommended leadership actions
- Deterministic escalation pattern briefing generator

No paid APIs or LLM calls are used. The recurrence logic and briefings are deterministic and explainable.

## Module B v2: Semantic Escalation Clustering and Structural Fix Cards

Module B v2 extends the deterministic recurrence detector with semantic clustering.

It uses:

- TF-IDF vectorization
- Cosine similarity
- Semantic cluster summaries
- Recurrence status classification
- Structural fix cards
- Weekly retro queue

This helps detect repeat escalation themes even when different teams describe the same operating breakdown using different wording.

The v2 Streamlit page is:

```text
pages/2_Module_B_v2_Semantic_Clusters.py
```

The main v2 files are:

- `src/escalation_semantic_clusters.py`
- `src/fix_cards.py`
- `docs/MODULE_B_V2_DEMO_SCRIPT.md`

Interview line:

> I built Module B in two layers. First, I used deterministic pattern keys for explainability. Then I added semantic clustering with TF-IDF so the system can detect recurring escalation patterns even when teams describe the same operating breakdown differently.

## Module C: Distributed Workforce Quality Scorer

Module C extends the command center into distributed workforce quality risk. It identifies coaching, calibration, training, staffing, and quality-system actions before quality drift becomes customer impact.

Module C answers:

1. Which teams or contributor cohorts show quality drift?
2. Which contributors need coaching, calibration, or training support?
3. Which work types have the highest distributed workforce quality risk?
4. Are quality issues linked to tenure, skill level, team, task complexity, rework, or reviewer disagreement?
5. Which quality-risk patterns should managers review in the weekly operating rhythm?
6. How do quality risks connect to Module A health degradation and Module B escalation recurrence?

Module C includes:

- Contributor-level quality feature builder
- Team-level quality feature builder
- Work-type-level quality rollup
- Deterministic quality risk scoring
- Recent/prior quality drift detection
- Weekly Coaching and Calibration Queue
- Contributor and team drilldowns
- Quality Coaching Card Generator
- Deterministic Module C weekly quality briefing

The Module C Streamlit page is:

```text
pages/3_Module_C_Workforce_Quality_Scorer.py
```

The main Module C files are:

- `src/workforce_quality.py`
- `src/quality_briefing.py`
- `docs/MODULE_C_HANDOFF.md`
- `docs/MODULE_C_DEMO_SCRIPT.md`

Important operating principle:

> Module C is not a punitive individual-ranking tool. It is a coaching, calibration, staffing, and quality-system risk detector.

## Module D: Capacity, Staffing, and SLA Forecasting

Module D extends the command center into capacity planning and next-week SLA protection. It helps a regional operations leader determine whether the region has enough trained capacity by work type, team, skill level, task complexity, backlog, and demand pattern.

Module D answers:

1. Which work types are at risk of capacity shortfall next week?
2. Which teams are over-utilized or under-utilized?
3. Where is SLA risk likely to emerge based on backlog, inflow, throughput, staffing, and task complexity?
4. Do we have enough skilled contributors for high-complexity or expert work?
5. Which staffing, cross-training, shift, or routing actions should managers take?
6. How do capacity risks connect to Module A health degradation, Module B recurring escalations, and Module C quality drift?
7. What should go into the weekly staffing and capacity review?

Module D includes:

- Work-type-level capacity feature builder
- Team-level capacity feature builder
- Skill/complexity capacity feature builder
- Deterministic capacity risk scoring
- Deterministic SLA forecast status classification
- Quality and escalation risk overlays
- Weekly Staffing and Capacity Review Queue
- Capacity Action Card Generator
- Deterministic Module D weekly staffing and capacity briefing

The Module D Streamlit page is:

```text
pages/4_Module_D_Capacity_SLA_Forecasting.py
```

The main Module D files are:

- `src/capacity_forecast.py`
- `src/capacity_briefing.py`
- `docs/MODULE_D_HANDOFF.md`
- `docs/MODULE_D_DEMO_SCRIPT.md`

Important operating principle:

> Module D is a capacity-planning, workload-balancing, SLA-protection, and quality-preservation system. It is not a productivity surveillance tool.

## Dashboard Questions

The dashboard is designed to answer:

1. Which work types are healthy or unhealthy this week?
2. Where are SLA, backlog, CSAT, quality, or escalation metrics degrading?
3. Which anomalies require leadership attention?
4. Which escalation patterns are recurring?
5. Which repeat escalation themes should go into the weekly ops retro?
6. Which teams, cohorts, or contributors are driving quality risk?
7. Which work types or teams face capacity shortfall or SLA risk next week?
8. What coaching, calibration, training, staffing, routing, or SOP action should happen next?
9. What weekly operating briefing should go to leadership?

## Project Structure

Key files and folders:

- `app.py` - Streamlit dashboard entry point for Module A and Module B v1
- `pages/2_Module_B_v2_Semantic_Clusters.py` - Module B v2 sidebar page
- `pages/3_Module_C_Workforce_Quality_Scorer.py` - Module C sidebar page
- `pages/4_Module_D_Capacity_SLA_Forecasting.py` - Module D sidebar page
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit local config
- `data/` - synthetic CSV data files
- `src/generate_data.py` - synthetic data generator
- `src/metrics.py` - KPI and metric calculations
- `src/rules.py` - health thresholds and anomaly rules
- `src/briefing.py` - deterministic weekly Module A briefing generator
- `src/escalation_patterns.py` - Module B recurrence scoring and pattern detection
- `src/escalation_briefing.py` - Module B deterministic briefing generator
- `src/escalation_semantic_clusters.py` - Module B v2 semantic clustering
- `src/fix_cards.py` - Module B v2 structural fix cards
- `src/workforce_quality.py` - Module C workforce quality risk scoring
- `src/quality_briefing.py` - Module C coaching cards and quality briefing
- `src/capacity_forecast.py` - Module D capacity, staffing, and SLA forecasting
- `src/capacity_briefing.py` - Module D capacity action cards and weekly briefing
- `src/charts.py` - Plotly chart helpers
- `docs/MODULE_B_HANDOFF.md` - Module B design and handoff notes
- `docs/MODULE_B_V2_DEMO_SCRIPT.md` - Module B v2 demo script
- `docs/MODULE_C_HANDOFF.md` - Module C design and handoff notes
- `docs/MODULE_C_DEMO_SCRIPT.md` - Module C demo script
- `docs/MODULE_D_HANDOFF.md` - Module D design and handoff notes
- `docs/MODULE_D_DEMO_SCRIPT.md` - Module D demo script
- `docs/FINAL_CHECKLIST.md` - final MVP checklist
- `docs/INTERVIEW_DEMO_SCRIPT.md` - interview walkthrough script

## Data Tables

The MVP uses seven synthetic CSV files:

1. `work_items.csv`
2. `teams.csv`
3. `contributors.csv`
4. `sla_events.csv`
5. `quality_events.csv`
6. `escalation_events.csv`
7. `csat_events.csv`

No real Scale AI data is used.

## Module B Input Contract

Module B uses:

```text
data/escalation_events.csv
```

Required fields:

- `escalation_id`
- `date`
- `work_type`
- `team_id`
- `severity`
- `customer_segment`
- `escalation_summary`
- `root_cause_category`
- `status`
- `days_to_resolve`

## Module C Input Contract

Module C uses:

```text
data/contributors.csv
data/quality_events.csv
data/work_items.csv
data/teams.csv
data/escalation_events.csv
```

Core fields:

- `contributor_id`
- `team_id`
- `work_item_id`
- `work_type`
- `region`
- `quality_score`
- `gold_task_pass`
- `reviewer_override`
- `peer_agreement_score`
- `rework_required`
- `task_complexity`
- `tenure_days`
- `skill_level`
- `location_type`
- `active_status`
- `customer_segment`
- `severity`
- `root_cause_category`
- `status`
- `days_to_resolve`

## Module D Input Contract

Module D uses:

```text
data/contributors.csv
data/quality_events.csv
data/work_items.csv
data/teams.csv
data/escalation_events.csv
data/sla_events.csv
```

Core fields:

- `contributor_id`
- `team_id`
- `work_item_id`
- `work_type`
- `region`
- `date_created`
- `date_completed`
- `status`
- `sla_due_at`
- `completed_at`
- `sla_met`
- `rework_required`
- `task_complexity`
- `tenure_days`
- `skill_level`
- `location_type`
- `active_status`
- `customer_segment`
- `severity`
- `root_cause_category`
- `days_to_resolve`
- `quality_score`
- `gold_task_pass`
- `reviewer_override`
- `peer_agreement_score`

If `work_items.csv` is missing or partial, Module D degrades gracefully by using available SLA, quality, contributor, and team data.

## Module B Pattern Keys

Module B can detect repeat patterns using four deterministic key grains:

- `work_type + root_cause_category`
- `work_type + team_id + root_cause_category`
- `customer_segment + work_type + root_cause_category`
- `team_id + severity + root_cause_category`

## Module B Risk Scoring

The recurrence score is deterministic:

```text
score = escalation_count * 2
      + sev1_count * 5
      + sev2_count * 3
      + open_count * 2
      + unique_customer_segments_impacted * 1.5
      + unresolved_or_slow_resolution_penalty
      + acceleration_bonus
```

Risk levels:

- `High recurrence risk`
- `Medium recurrence risk`
- `Low recurrence risk`

Pattern statuses:

- `New`
- `Recurring`
- `Accelerating`
- `Dormant`
- `Resolved`
- `Watchlist`
- `Low activity`

## Module C Risk Scoring

Contributor risk score is deterministic:

```text
risk_score = quality_score_gap
           + gold_task_fail_penalty
           + reviewer_override_penalty
           + peer_agreement_penalty
           + rework_penalty
           + quality_drop_penalty
           + low_tenure_complexity_penalty
           + low_sample_size_adjustment
```

Team risk score is deterministic:

```text
team_risk_score = avg_quality_gap
                + gold_task_fail_rate_penalty
                + reviewer_override_rate_penalty
                + rework_rate_penalty
                + high_risk_contributor_count_penalty
                + low_tenure_share_penalty
                + quality_drift_penalty
```

Risk levels:

- `High quality risk`
- `Medium quality risk`
- `Low quality risk`
- `Insufficient sample`

## Module D Risk Scoring

Work-type capacity risk score is deterministic:

```text
capacity_risk_score = backlog_pressure_penalty
                    + aged_backlog_penalty
                    + throughput_gap_penalty
                    + sla_miss_penalty
                    + utilization_penalty
                    + high_complexity_capacity_penalty
                    + rework_capacity_drag_penalty
                    + escalation_overlay_penalty
                    + quality_overlay_penalty
```

Team capacity risk score adds:

```text
low_tenure_high_complexity_penalty
junior_high_complexity_mismatch_penalty
```

Risk levels:

- `High capacity risk`
- `Medium capacity risk`
- `Low capacity risk`
- `Insufficient data`

SLA forecast statuses:

- `SLA likely stable`
- `SLA watchlist`
- `SLA at risk`
- `SLA recovery needed`
- `Insufficient data`

## Command Center Front-End (`web/`)

`web/` contains the canonical front-end — a TanStack Start / React + TypeScript
app (shadcn/ui), ported from the Lovable project, wired to the same data and
scoring logic as the Streamlit app. It builds to a static SPA (Vite) and fetches
all numbers client-side from `web/public/data/*.json`; every view *reads*
precomputed scores and never recomputes them.

Regenerate the data payload after any change to the CSVs in `data/`:

```bash
python -m src.build_frontend_data        # writes web/public/data/data.json
```

The builder reuses `src/metrics.py` and `src/escalation_patterns.py`, so the
KPIs, pattern risk scores, and recurrence statuses in the React view match the
Streamlit pages exactly.

Run it locally (dev server, or build + preview the static output):

```bash
cd web
bun install
bun run dev                       # http://localhost:8080  (live dev)
# or verify the deployed artifact:  bun run build && bun run preview
```

On Render the primary service is a **static site** that builds `web/` and serves
`web/dist/client` (SPA fallback to `index.html`); see `render.yaml`. The
Streamlit app remains the analyst workbench with the full Module C/D drilldowns
and is run locally with `streamlit run app.py`.

## Data Pipeline

The pipeline regenerates the synthetic CSVs and rebuilds the frontend JSON in
one command, for one or all scenarios. Each scenario (`healthy`, `current`,
`crisis`) scales the underlying SLA, quality, CSAT, rework, and escalation
rates, so the dashboard visibly changes when you switch between them — useful
for a live demo.

```bash
# Generate all scenarios (writes data-healthy/current/crisis.json + data.json)
python -m src.pipeline --all-scenarios

# Generate one scenario
python -m src.pipeline --scenario crisis
```

The orchestrator runs `generate_data` then `build_frontend_data` per scenario,
prints a manifest table (escalations, patterns, teams, generated-at per
scenario), and validates every emitted JSON (required keys present, escalation
and pattern counts non-zero). Each JSON carries pipeline metadata:
`generated_at`, `scenario`, `pipeline_version`, and `row_counts`.

## Production Architecture

[docs/PRODUCTION_ARCHITECTURE.md](docs/PRODUCTION_ARCHITECTURE.md) describes how
this prototype maps onto a production pipeline: source-system extract adapters
feeding the same `src/` scoring engine on a schedule, emitting to a database or
API for the Aurora and Streamlit surfaces. The key point is that the `src/`
modules stay unchanged — only the data source, scheduling, storage, and auth
layers change — and the 83-test suite locks that scoring contract.

## How to Run Locally

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## Run and Validate

Validate Python syntax:

```bash
python -m py_compile app.py src/*.py pages/*.py
```

Run the Streamlit app:

```bash
python -m streamlit run app.py
```

## Run Tests

Install the dev dependencies and run the smoke test suite:

```bash
pip install -r requirements-dev.txt
pytest -q
```

The tests cover metric calculations (`src/metrics.py`), health threshold
boundaries (`src/rules.py`), workforce quality risk scoring
(`src/workforce_quality.py`), and capacity forecasting
(`src/capacity_forecast.py`). They use small hand-built DataFrames and do
not import Streamlit.

## Demo Materials

- Module B handoff: `docs/MODULE_B_HANDOFF.md`
- Module B v2 demo script: `docs/MODULE_B_V2_DEMO_SCRIPT.md`
- Module C handoff: `docs/MODULE_C_HANDOFF.md`
- Module C demo script: `docs/MODULE_C_DEMO_SCRIPT.md`
- Module D handoff: `docs/MODULE_D_HANDOFF.md`
- Module D demo script: `docs/MODULE_D_DEMO_SCRIPT.md`
- Final checklist: `docs/FINAL_CHECKLIST.md`
- Interview demo script: `docs/INTERVIEW_DEMO_SCRIPT.md`

## Live Demo

Deployed app:

https://ops-prototype-dashboards.onrender.com

Demo path:

1. Open the main app.
2. Review Module A executive KPIs and health heatmap.
3. Scroll to Module B v1 recurrence detector.
4. Open sidebar page: 2 Module B v2 Semantic Clusters.
5. Review semantic cluster summary, structural fix card, and weekly retro queue.
6. Open sidebar page: 3 Module C Workforce Quality Scorer.
7. Review contributor/team quality risk, drilldowns, weekly coaching queue, and coaching card generator.
8. Open sidebar page: 4 Module D Capacity SLA Forecasting.
9. Review capacity risk, SLA forecast, team/work-type drilldowns, weekly staffing queue, and capacity action cards.

## Future Extensions

Recommended next enhancements:

- Expand `data/escalation_events.csv` to 150-300 synthetic records for richer recurrence scenarios
- Export `data/escalation_pattern_summary.csv`
- Export `data/workforce_quality_summary.csv`
- Export `data/contributor_quality_risk.csv`
- Export `data/capacity_forecast_summary.csv`
- Export `data/team_capacity_risk.csv`
- Export `data/work_type_capacity_risk.csv`
- Add SQLite or DuckDB
- Add authentication if deployed
- Add automated weekly report export
- Add LLM-powered narrative generation after deterministic baseline is trusted
