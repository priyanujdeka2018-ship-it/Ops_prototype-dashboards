# Phase 1: Data Model and Synthetic Data Plan

This document defines the data model, table relationships, metric definitions, health thresholds, and synthetic data design for the Scale Regional Ops Health Dashboard.

## Tables

| Table | Purpose |
|---|---|
| `work_items` | Primary fact table. One row per operational task. |
| `teams` | One row per operating team. |
| `contributors` | One row per contributor. |
| `sla_events` | SLA outcome and delay reason tracking. |
| `quality_events` | Quality review and calibration signals. |
| `escalation_events` | Customer/internal escalation tracking. |
| `csat_events` | Customer satisfaction signals. |

## Work Item Columns

`work_item_id`, `date_created`, `date_completed`, `region`, `work_type`, `team_id`, `contributor_id`, `customer_segment`, `priority`, `status`, `sla_due_at`, `completed_at`, `sla_met`, `rework_required`, `task_complexity`

## Team Columns

`team_id`, `region`, `city`, `manager_name`, `work_type`, `active_contributors`, `shift_type`

## Contributor Columns

`contributor_id`, `team_id`, `tenure_days`, `skill_level`, `location_type`, `active_status`

## SLA Event Columns

`event_id`, `work_item_id`, `due_at`, `completed_at`, `sla_met`, `delay_hours`, `delay_reason`

## Quality Event Columns

`quality_event_id`, `work_item_id`, `contributor_id`, `reviewer_id`, `quality_score`, `gold_task_pass`, `reviewer_override`, `peer_agreement_score`

## Escalation Event Columns

`escalation_id`, `date`, `work_type`, `team_id`, `severity`, `customer_segment`, `escalation_summary`, `root_cause_category`, `status`, `days_to_resolve`

## CSAT Event Columns

`csat_id`, `date`, `work_type`, `team_id`, `customer_segment`, `csat_score`, `feedback_theme`

## Relationships

```text
teams.team_id
  -> contributors.team_id
  -> work_items.team_id

contributors.contributor_id
  -> work_items.contributor_id
  -> quality_events.contributor_id

work_items.work_item_id
  -> sla_events.work_item_id
  -> quality_events.work_item_id

teams.team_id
  -> escalation_events.team_id
  -> csat_events.team_id
```

## Metric Definitions

| Metric | Definition |
|---|---|
| SLA adherence % | Completed items with `sla_met=True` divided by completed items. |
| Backlog count | Items with status in queued, in_progress, or blocked. |
| Aged backlog >72 hours | Open items older than 72 hours. |
| CSAT trailing 7-day average | Average CSAT score over last 7 days. |
| Escalation rate per 1,000 | Escalation count divided by work item count times 1,000. |
| Average quality score | Mean of `quality_score`. |
| Rework rate | Items with `rework_required=True` divided by completed items. |
| FCR proxy | Completed items with `sla_met=True` and `rework_required=False` divided by completed items. |

## Health Thresholds

| Metric | Green | Amber | Red |
|---|---:|---:|---:|
| SLA adherence | >= 95% | 90% to 94.9% | < 90% |
| CSAT | >= 4.4 | 4.2 to 4.39 | < 4.2 |
| Quality score | >= 90 | 85 to 89.9 | < 85 |
| Rework rate | <= 6% | >6% to 10% | >10% |
| Escalation rate per 1,000 | <= 8 | >8 to 15 | >15 |
| Aged backlog >72h | <= 25 | 26 to 60 | >60 |

## Synthetic Operating Scenarios

1. `image_annotation`: healthy baseline.
2. `rlhf_evaluation`: SLA and CSAT degradation in the last two weeks.
3. `code_review`: quality decline and rework spike.
4. `audio_evaluation`: aged backlog pressure.
5. `expert_review`: low volume but high-severity escalation risk.

The synthetic data will be generated deterministically with `np.random.seed(42)`.
