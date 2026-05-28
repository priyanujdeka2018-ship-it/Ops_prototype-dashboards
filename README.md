# Scale Regional Ops Command Center

## Module A: Regional Operations Health Dashboard

**Current status: Module A MVP complete.**

This repository contains an interview-ready Streamlit prototype for a Scale AI Operations / Regional Lead style role.

The dashboard gives a regional operations leader one operating view across:

- SLA adherence
- CSAT
- Backlog
- Aged backlog over 72 hours
- Escalation rate
- Quality score
- Rework rate
- First-contact-resolution proxy

The MVP includes:

- Executive KPI tiles
- Regional health heatmap
- Work type drilldown
- Team drilldown
- Rule-based anomaly detection
- Weekly ops briefing generator
- Synthetic data only
- Interview demo script
- Final MVP checklist

## Interview Positioning

> In my first 60 days, I would want a single regional operating view that surfaces SLA, backlog, CSAT, quality, and escalation risk before customer impact lands. I built this prototype to show the operating system I would bring to the role.

## MVP Scope

This repo currently focuses only on Module A:

- Regional Operations Health Dashboard

Future modules, intentionally not built yet:

- Module B: Escalation Pattern Recurrence Detector
- Module C: Distributed Workforce Quality Scorer

## Dashboard Questions

The dashboard is designed to answer:

1. Which work types are healthy or unhealthy this week?
2. Where are SLA, backlog, CSAT, quality, or escalation metrics degrading?
3. Which anomalies require leadership attention?
4. What weekly operating briefing should go to leadership?
5. What action should frontline managers take?

## Project Structure

Key files and folders:

- `app.py` — Streamlit dashboard entry point
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — Streamlit local config
- `data/` — synthetic CSV data files
- `src/generate_data.py` — synthetic data generator
- `src/metrics.py` — KPI and metric calculations
- `src/rules.py` — health thresholds and anomaly rules
- `src/briefing.py` — deterministic weekly briefing generator
- `src/charts.py` — Plotly chart helpers
- `docs/FINAL_CHECKLIST.md` — final MVP checklist
- `docs/INTERVIEW_DEMO_SCRIPT.md` — interview walkthrough script

## Phase Plan

### Phase 1: Data model and synthetic data generation plan

Define the operating model, data tables, metrics, thresholds, synthetic scenarios, and project scaffold.

### Phase 2: Generate synthetic data

Create realistic synthetic CSV data across work items, teams, contributors, SLA events, quality events, escalations, and CSAT.

### Phase 3: Metric calculations

Build reusable metric functions for SLA, backlog, CSAT, quality, rework, first-contact-resolution proxy, and escalation rate.

### Phase 4: Streamlit UI

Build the executive dashboard, health heatmap, work type drilldown, and team drilldown.

### Phase 5: Anomaly detection

Add deterministic anomaly rules for SLA drops, CSAT dips, backlog spikes, escalation spikes, quality declines, and rework increases.

### Phase 6: Weekly ops briefing

Generate a structured weekly leadership briefing using deterministic templates.

### Phase 7: Interview demo script

Add a walkthrough script that explains the prototype in a Scale AI Operations / Regional Lead interview context.

## Data Tables

The MVP will use seven synthetic CSV files:

1. `work_items.csv`
2. `teams.csv`
3. `contributors.csv`
4. `sla_events.csv`
5. `quality_events.csv`
6. `escalation_events.csv`
7. `csat_events.csv`

No real Scale AI data is used.

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

Install dependencies:

```bash
pip install -r requirements.txt
python -m py_compile app.py src/*.py
