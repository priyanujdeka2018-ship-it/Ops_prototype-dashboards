# Scale Regional Ops Command Center

## Current Status

**Module A MVP complete. Module B MVP added.**

This repository contains an interview-ready Streamlit prototype for a Scale AI Operations / Regional Lead style role.

The command center now includes:

1. **Module A: Regional Operations Health Dashboard**
2. **Module B: Escalation Pattern Recurrence Detector**

Module C is intentionally not built yet:

- **Module C: Distributed Workforce Quality Scorer**

## Interview Positioning

> In my first 60 days, I would want a single regional operating view that surfaces SLA, backlog, CSAT, quality, and escalation risk before customer impact lands. I built this prototype to show the operating system I would bring to the role.

Module B extends that story:

> Module A tells me where regional health is degrading. Module B tells me whether escalations are isolated incidents or recurring operating-system failures. This helps leadership move from reactive escalation handling to pattern-based prevention.

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

## Module B: Escalation Pattern Recurrence Detector

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

## Dashboard Questions

The dashboard is designed to answer:

1. Which work types are healthy or unhealthy this week?
2. Where are SLA, backlog, CSAT, quality, or escalation metrics degrading?
3. Which anomalies require leadership attention?
4. Which escalation patterns are recurring?
5. Which repeat escalation themes should go into the weekly ops retro?
6. What weekly operating briefing should go to leadership?
7. What action should frontline managers take?

## Project Structure

Key files and folders:

- `app.py` — Streamlit dashboard entry point for Modules A and B
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — Streamlit local config
- `data/` — synthetic CSV data files
- `src/generate_data.py` — synthetic data generator
- `src/metrics.py` — KPI and metric calculations
- `src/rules.py` — health thresholds and anomaly rules
- `src/briefing.py` — deterministic weekly Module A briefing generator
- `src/escalation_patterns.py` — Module B recurrence scoring and pattern detection
- `src/escalation_briefing.py` — Module B deterministic briefing generator
- `src/charts.py` — Plotly chart helpers
- `docs/MODULE_B_HANDOFF.md` — Module B design and handoff notes
- `docs/FINAL_CHECKLIST.md` — final MVP checklist
- `docs/INTERVIEW_DEMO_SCRIPT.md` — interview walkthrough script

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

## Module B Pattern Keys

Module B can detect repeat patterns using four deterministic key grains:

- `work_type + root_cause_category`
- `work_type + team_id + root_cause_category`
- `customer_segment + work_type + root_cause_category`
- `team_id + severity + root_cause_category`

This lets the user move from broad systemic recurrence to narrower team/customer drilldowns.

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
python -m py_compile app.py src/*.py
```

Run the Streamlit app:

```bash
python -m streamlit run app.py
```

## Demo Materials

- Module B handoff: `docs/MODULE_B_HANDOFF.md`
- Final checklist: `docs/FINAL_CHECKLIST.md`
- Interview demo script: `docs/INTERVIEW_DEMO_SCRIPT.md`

## Future Extensions

Recommended next enhancements:

- Expand `data/escalation_events.csv` to 150–300 synthetic records for richer recurrence scenarios
- Export `data/escalation_pattern_summary.csv`
- Add semantic clustering using TF-IDF or sentence embeddings
- Add Module C: Distributed Workforce Quality Scorer
- Add SQLite or DuckDB
- Add authentication if deployed
- Add automated weekly report export
- Add LLM-powered narrative generation after deterministic baseline is trusted
