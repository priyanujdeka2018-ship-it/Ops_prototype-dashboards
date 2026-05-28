# Final MVP Checklist

## Phase Completion

### Module A: Regional Operations Health Dashboard

- [x] Phase 1: Data model and project scaffold
- [x] Phase 2: Synthetic data generation
- [x] Phase 3: Metric calculations
- [x] Phase 4: Streamlit UI
- [x] Phase 5: Anomaly detection panel
- [x] Phase 6: Weekly ops briefing generator
- [x] Phase 7: README cleanup and interview demo script

### Module B v1: Escalation Pattern Recurrence Detector

- [x] Phase B1: Escalation pattern data model
- [x] Phase B2: Pattern detection logic in `src/escalation_patterns.py`
- [x] Phase B3: Pattern briefing logic in `src/escalation_briefing.py`
- [x] Phase B4: Streamlit UI integration in `app.py`
- [x] Phase B5: README, handoff, checklist, and demo-script updates

### Module B v2: Semantic Escalation Clustering and Structural Fix Cards

- [x] Confirm `src/escalation_semantic_clusters.py` exists
- [x] Confirm `src/fix_cards.py` exists
- [x] Confirm `pages/2_Module_B_v2_Semantic_Clusters.py` exists
- [x] Confirm `scikit-learn` is in `requirements.txt`
- [x] Confirm semantic cluster summary renders
- [x] Confirm cluster drilldown renders
- [x] Confirm structural fix card renders
- [x] Confirm weekly retro queue renders

### Module C: Distributed Workforce Quality Scorer

- [x] Phase C1: Workforce quality data model in `src/workforce_quality.py`
- [x] Phase C2: Contributor and team risk scoring
- [x] Phase C3: Quality coaching card generator in `src/quality_briefing.py`
- [x] Phase C4: Streamlit sidebar page in `pages/3_Module_C_Workforce_Quality_Scorer.py`
- [x] Phase C5: README, checklist, handoff, and demo-script updates

## Demo Readiness

Before the interview demo, run:

```bash
python -m py_compile app.py src/*.py pages/*.py
python -m streamlit run app.py
```

Confirm these Module A sections render:

- [ ] Executive KPI Tiles
- [ ] Regional Health Heatmap
- [ ] Anomaly Detection Panel
- [ ] Weekly Ops Briefing Generator
- [ ] Work Type Drilldown
- [ ] Team Drilldown

Confirm these Module B v1 sections render:

- [ ] Recurring Escalation Pattern Summary
- [ ] Top Repeat Root Causes
- [ ] Pattern Risk Table
- [ ] Pattern Drilldown
- [ ] Recommended Leadership Actions
- [ ] Escalation Pattern Briefing Generator

Confirm these Module B v2 sections render:

- [ ] Sidebar page: 2 Module B v2 Semantic Clusters
- [ ] Semantic Cluster Summary
- [ ] Cluster Charts
- [ ] Cluster Drilldown
- [ ] Structural Fix Card
- [ ] Weekly Retro Queue

Confirm these Module C sections render:

- [ ] Sidebar page: 3 Module C Workforce Quality Scorer
- [ ] Executive Workforce Quality Summary
- [ ] Contributor Quality Risk Table
- [ ] Team Quality Risk Table
- [ ] Quality Drift View
- [ ] Contributor Drilldown
- [ ] Team Drilldown
- [ ] Weekly Coaching and Calibration Queue
- [ ] Quality Coaching Card Generator
- [ ] Module C Weekly Briefing

## Demo Talk Track

Core Module A sentence:

> “In my first 60 days, I would want a single regional operating view that surfaces SLA, backlog, CSAT, quality, and escalation risk before customer impact lands. I built this prototype to show the operating system I would bring to the role.”

Core Module B sentence:

> “Module A tells me where regional health is degrading. Module B tells me whether escalations are isolated incidents or recurring operating-system failures. This helps leadership move from reactive escalation handling to pattern-based prevention.”

Core Module C sentence:

> “I do not want to use quality data as a punitive scoreboard. I want to use it as an operating signal. Module C identifies where quality risk is emerging across teams, cohorts, and work types, then turns that signal into coaching and calibration actions.”

## What To Emphasize

- [ ] Synthetic data only; no real Scale AI data
- [ ] Deterministic rules before LLM summarization
- [ ] Regional health view across work types
- [ ] Drilldown from region to work type to team
- [ ] Weekly leadership briefing
- [ ] Recurring escalation pattern detection
- [ ] Pattern-risk scoring based on recurrence, severity, open count, customer blast radius, acceleration, and slow resolution
- [ ] Semantic clustering catches repeated issues with different wording
- [ ] Structural fix cards convert recurring escalations into leadership decisions
- [ ] Workforce quality risk is for coaching, calibration, training, staffing, and SOP action
- [ ] Weekly Coaching and Calibration Queue is not a punitive leaderboard
- [ ] Quality coaching cards define owner, metric, decision, and follow-up date

## Module B Validation Checklist

- [ ] `src/escalation_patterns.py` imports successfully
- [ ] `src/escalation_briefing.py` imports successfully
- [ ] `summarize_patterns()` returns a DataFrame with `pattern_id`, `pattern_key`, `recurrence_status`, `risk_score`, `risk_level`, and `recommended_action`
- [ ] Pattern key selector changes the aggregation grain
- [ ] Module B filters work for work type, team, customer segment, severity, root cause, and status
- [ ] Pattern drilldown shows recent escalation summaries
- [ ] Escalation pattern briefing downloads as markdown

## Module C Validation Checklist

- [ ] `src/workforce_quality.py` imports successfully
- [ ] `src/quality_briefing.py` imports successfully
- [ ] `build_contributor_quality_features()` returns contributor risk rows
- [ ] `build_team_quality_features()` returns team risk rows
- [ ] `build_work_type_quality_features()` returns work-type risk rows
- [ ] `get_weekly_quality_review_queue()` returns coaching and calibration queue rows
- [ ] Contributor filters work for work type, team, skill level, location type, and risk level
- [ ] Contributor drilldown shows quality evidence and task-complexity mix
- [ ] Team drilldown shows quality trend, top risk drivers, and recent quality events
- [ ] Coaching card generator renders cards for contributor and team subjects
- [ ] Module C weekly briefing downloads as markdown

## Future Enhancements

- [ ] Expand `data/escalation_events.csv` to 150–300 synthetic records
- [ ] Export `data/escalation_pattern_summary.csv`
- [x] Add semantic similarity using TF-IDF; future upgrade can use sentence embeddings
- [x] Add Module C: Distributed Workforce Quality Scorer
- [ ] Export `data/workforce_quality_summary.csv`
- [ ] Export `data/contributor_quality_risk.csv`
- [ ] Add SQLite or DuckDB
- [ ] Add authentication if deployed
- [ ] Add automated weekly report export
- [ ] Add LLM-powered narrative generation after deterministic baseline is trusted
