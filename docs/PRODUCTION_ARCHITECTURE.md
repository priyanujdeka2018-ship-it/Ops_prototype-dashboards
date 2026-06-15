# Production Architecture

How this interview prototype maps onto a real production data pipeline, and
what would change versus what already carries over unchanged.

## Current prototype

```
generate_data.py → CSVs → build_frontend_data.py → data-{scenario}.json → Aurora
                     │
                     └────────── same src/ engine ──────────→ Streamlit analyst view
```

A single `python -m src.pipeline --all-scenarios` run generates the synthetic
CSVs, scores them with the `src/` engine, and emits one JSON payload per
scenario for the Aurora front-end. The same `src/` modules back the Streamlit
analyst view, so both surfaces report identical numbers.

## Production path

```
Source Systems              Scheduled Pipeline            Presentation
┌───────────────┐    ┌──────────────────────────┐    ┌───────────────┐
│ Labeling plat │    │ Airflow / cron / Lambda   │    │ Aurora exec   │
│ QA system     │───▶│  1. Extract → DataFrames  │───▶│ Streamlit     │
│ Ticketing     │    │  2. src/ scoring engine   │    │ analyst view  │
│ CSAT surveys  │    │  3. Emit JSON / write DB  │    └───────────────┘
│ Workforce DB  │    │  4. Validate + alert      │
└───────────────┘    └──────────────────────────┘
```

The synthetic `generate_data.py` step is replaced by extract adapters that pull
from real source systems into the same DataFrame shapes. Everything downstream
of "DataFrames" is already what runs today.

## What changes vs what stays

- **STAYS:** all `src/` modules — `metrics`, `rules`, `workforce_quality`,
  `escalation_patterns`, `capacity_forecast`. They accept DataFrames and return
  scored results, with no I/O or framework coupling. 83 tests guard them, so
  the scoring contract is locked regardless of where the data comes from.
- **CHANGES:** the data-source adapter (CSV → SQL/warehouse/API), scheduling
  (manual CLI → cron/Airflow/Lambda), storage (JSON files on disk → database or
  served API), and an auth layer in front of the presentation tier.

## Scaling dimensions

- **Data volume:** swap CSV reads for paginated warehouse queries. The scoring
  functions are already vectorized pandas, so the change is at the I/O edge, not
  in the engine.
- **Multi-region:** run one parameterized pipeline pass per region. The region
  picker already exists in Aurora; production just points each region at its own
  payload.
- **Real-time:** the batch pipeline stays for weekly review. Add a lightweight
  websocket listener for live escalation alerts alongside it, without touching
  the batch path.
- **Refresh cadence:** the prototype is on-demand. Production runs on an
  hourly/daily schedule with staleness monitoring — the `generated_at` timestamp
  already in every payload is the hook for that freshness check.
