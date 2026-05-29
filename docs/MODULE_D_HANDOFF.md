# Module D Handoff: Capacity, Staffing, and SLA Forecasting

## Module Goal

Module D extends the Scale Regional Ops Command Center from health, escalation recurrence, and workforce quality into capacity and SLA forecasting.

It answers:

1. Which work types are at risk of capacity shortfall next week?
2. Which teams are over-utilized or under-utilized?
3. Where is SLA risk likely to emerge based on backlog, inflow, throughput, staffing, and task complexity?
4. Do we have enough skilled contributors for high-complexity or expert work?
5. Which staffing, cross-training, shift, or routing actions should managers take?
6. How do capacity risks connect to Module A health degradation, Module B recurring escalations, and Module C quality drift?
7. What should go into the weekly staffing and capacity review?

Operating principle:

> Module D is a capacity-planning, workload-balancing, SLA-protection, and quality-preservation system. It is not a productivity surveillance tool.

## New Files

```text
src/capacity_forecast.py
src/capacity_briefing.py
pages/4_Module_D_Capacity_SLA_Forecasting.py
docs/MODULE_D_HANDOFF.md
docs/MODULE_D_DEMO_SCRIPT.md
```

## Data Sources

Module D uses synthetic command-center data only:

```text
data/contributors.csv
data/quality_events.csv
data/work_items.csv
data/teams.csv
data/escalation_events.csv
data/csat_events.csv
data/sla_events.csv
```

No real Scale AI data is used.

The preferred path uses `work_items.csv` as the primary work-item grain. If `work_items.csv` is missing, blank, or partial, `prepare_capacity_data()` degrades gracefully by using SLA events plus available contributor, team, quality, and escalation data.

## Core Code Entry Points

`src/capacity_forecast.py` exposes:

```text
prepare_capacity_data(...)
build_work_type_capacity_features(...)
build_team_capacity_features(...)
build_skill_complexity_capacity_features(...)
score_work_type_capacity_risk(...)
score_team_capacity_risk(...)
classify_sla_forecast_status(...)
recommend_capacity_action(...)
get_weekly_capacity_review_queue(...)
build_capacity_trend(...)
```

`src/capacity_briefing.py` exposes:

```text
generate_capacity_action_card(...)
format_capacity_action_card_markdown(...)
generate_capacity_review_briefing(...)
```

## Work-Type Capacity Features

The work-type summary includes:

```text
work_type
region
open_backlog
aged_backlog_72h
new_items_7d
completed_items_7d
completed_items_14d
avg_daily_inflow_7d
avg_daily_throughput_7d
throughput_gap
estimated_days_to_clear_backlog
sla_adherence_7d
sla_miss_rate_7d
rework_rate_7d
avg_task_complexity_score
high_complexity_share
expert_complexity_share
active_contributors
available_contributors
capacity_units
required_capacity_units
capacity_gap
utilization_rate
forecasted_sla_risk
capacity_risk_score
capacity_risk_level
recommended_capacity_action
```

## Team Capacity Features

The team summary includes:

```text
team_id
work_type
region
manager_name
active_contributors
available_contributors
open_backlog
aged_backlog_72h
new_items_7d
completed_items_7d
avg_daily_inflow_7d
avg_daily_throughput_7d
throughput_gap
estimated_days_to_clear_backlog
sla_adherence_7d
sla_miss_rate_7d
rework_rate_7d
high_complexity_share
expert_complexity_share
junior_share
low_tenure_share
capacity_units
required_capacity_units
capacity_gap
utilization_rate
quality_risk_overlay
escalation_risk_overlay
capacity_risk_score
capacity_risk_level
recommended_manager_action
```

## Skill / Complexity Capacity Features

The skill-complexity summary includes:

```text
work_type
skill_level
task_complexity
active_contributors
completed_items_7d
open_backlog
sla_miss_rate_7d
rework_rate_7d
quality_score
capacity_gap
risk_level
recommended_action
```

## Deterministic Risk Scoring

Module D uses explainable deterministic scoring. It does not call paid APIs or external ML services.

Work-type capacity risk combines:

```text
backlog pressure
aged backlog over 72h
throughput gap
SLA miss rate
utilization above safe threshold
high-complexity work mix
expert complexity demand
rework capacity drag
recurring escalation overlay
quality risk overlay
```

Team capacity risk adds:

```text
low-tenure plus high-complexity mismatch
junior-heavy plus high-complexity mismatch
```

Risk levels:

```text
High capacity risk
Medium capacity risk
Low capacity risk
Insufficient data
```

## SLA Forecast Statuses

SLA forecast status is deterministic:

```text
SLA likely stable
SLA watchlist
SLA at risk
SLA recovery needed
Insufficient data
```

Forecast rules inspect:

```text
open backlog
aged backlog over 72h
recent inflow trend
recent completion throughput
SLA adherence
available contributor capacity
task complexity mix
rework drag
quality risk overlay
recurring escalation overlay
```

## Action Mapping

Module D maps capacity drivers to manager-ready actions:

| Risk driver | Recommended action |
| --- | --- |
| Backlog growing faster than throughput | Add short-term staffing or reroute work |
| Aged backlog over threshold | Backlog burn-down sprint |
| SLA miss rate rising | Manager SLA recovery plan |
| Utilization above safe threshold | Add coverage / rebalance workload |
| High-complexity work concentrated in low-tenure team | Shift complex work to senior contributors + training ramp |
| High rework drag | Quality + workflow review before adding volume |
| Recurring escalation overlay | Structural fix owner required before scaling volume |
| Quality risk overlay | Pair capacity action with calibration/coaching |
| Underutilized team | Cross-route work from overloaded queue |
| Expert capacity shortfall | Cross-train senior contributors / request specialist coverage |

## Streamlit Page

The new sidebar page is:

```text
pages/4_Module_D_Capacity_SLA_Forecasting.py
```

It includes:

1. Executive Capacity and SLA Forecast Summary
2. Work-Type Capacity Risk Table
3. Team Capacity Risk Table
4. Capacity Forecast View
5. Team / Work-Type Drilldown
6. Weekly Staffing and Capacity Review Queue
7. Capacity Action Card Generator
8. Module D Weekly Staffing and Capacity Briefing

## Integration With Module A

Module A shows where operational health is degrading.

Module D explains whether the degradation is caused by:

```text
capacity
staffing
throughput
backlog
complexity
utilization pressure
```

Demo line:

> Module A shows audio evaluation SLA and backlog pressure. Module D lets me inspect whether the issue is caused by rising inflow, insufficient throughput, aged backlog, high complexity mix, or team-level capacity imbalance.

## Integration With Module B

Module B shows recurring escalation patterns.

Module D explains whether recurring escalations are linked to:

```text
capacity shortfall
backlog pressure
SLA miss risk
unresolved staffing constraints
workflow handoff gaps
```

Demo line:

> Module B shows recurring capacity shortfall escalations in RLHF evaluation. Module D lets me check whether the pattern is tied to inflow growth, insufficient throughput, undercoverage, or high utilization.

## Integration With Module C

Module C shows quality and coaching risk.

Module D explains whether quality risk is creating capacity drag through:

```text
rework
calibration load
low-tenure/high-complexity mismatch
reviewer coverage gaps
```

Demo line:

> Module C shows quality drift in code review. Module D lets me check whether that quality drift is also reducing effective capacity through rework and whether staffing should be adjusted before SLA misses increase.

## Validation

Run:

```bash
python -m py_compile app.py src/*.py pages/*.py
python -m streamlit run app.py
```

Confirm:

- Work-type capacity table renders
- Team capacity table renders
- Skill/complexity capacity table renders
- Weekly staffing and capacity review queue renders
- Capacity action card generator renders
- Module D weekly briefing downloads
- Filters work for work type, team, region, skill level, complexity, and risk level
- Drilldowns work for work type and team

## Definition of Done

- [x] Work-type capacity-risk summary is generated
- [x] Team capacity-risk summary is generated
- [x] Skill/complexity capacity summary is generated
- [x] Weekly staffing and capacity review queue is generated
- [x] Capacity action card generator works
- [x] Streamlit Module D page renders from sidebar
- [x] Drilldowns exist for work type and team
- [x] README and demo scripts are updated
- [ ] Live Render deployment confirmed after merge
