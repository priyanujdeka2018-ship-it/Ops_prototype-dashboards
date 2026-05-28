# Module C Handoff: Distributed Workforce Quality Scorer

## Status

Module C is implemented as the third command-center module.

It extends the prototype from regional health and escalation recurrence into distributed workforce quality risk. The module is deliberately framed as a coaching, calibration, training, staffing, and quality-system detector, not as a punitive individual ranking tool.

## Business Question

Module C answers:

1. Which teams or contributor cohorts show quality drift?
2. Which contributors need coaching, calibration, or training support?
3. Which work types have the highest distributed workforce quality risk?
4. Are quality issues linked to tenure, skill level, team, task complexity, rework, or reviewer disagreement?
5. Which quality-risk patterns should managers review in the weekly operating rhythm?
6. How do quality risks connect to Module A health degradation and Module B escalation recurrence?

## Files Added

- `src/workforce_quality.py`
- `src/quality_briefing.py`
- `pages/3_Module_C_Workforce_Quality_Scorer.py`
- `docs/MODULE_C_HANDOFF.md`
- `docs/MODULE_C_DEMO_SCRIPT.md`

## Input Data

Module C reuses the synthetic command-center data:

- `data/contributors.csv`
- `data/quality_events.csv`
- `data/work_items.csv`
- `data/teams.csv`
- `data/escalation_events.csv`
- `data/csat_events.csv`
- `data/sla_events.csv`

No real Scale AI data is used.

The scorer is resilient to partial synthetic data. If `work_items.csv` is empty or missing, Module C still uses `quality_events.csv`, `contributors.csv`, and `teams.csv` to infer team and work-type context, while assigning conservative defaults for task complexity and rework.

## Core Functions

`src/workforce_quality.py` contains:

- `prepare_quality_data(...)`
- `build_contributor_quality_features(...)`
- `build_team_quality_features(...)`
- `build_work_type_quality_features(...)`
- `score_contributor_quality_risk(...)`
- `score_team_quality_risk(...)`
- `classify_quality_status(...)`
- `recommend_quality_action(...)`
- `get_weekly_quality_review_queue(...)`
- `build_quality_trend(...)`

`src/quality_briefing.py` contains:

- `generate_quality_coaching_card(...)`
- `format_quality_coaching_card_markdown(...)`
- `generate_quality_review_briefing(...)`

## Contributor Feature Model

For each contributor, Module C calculates:

- `contributor_id`
- `team_id`
- `work_type`
- `skill_level`
- `tenure_days`
- `location_type`
- `active_status`
- `completed_items`
- `sampled_quality_events`
- `avg_quality_score`
- `gold_task_fail_rate`
- `reviewer_override_rate`
- `avg_peer_agreement_score`
- `rework_rate`
- `high_complexity_share`
- `expert_complexity_share`
- `recent_quality_score`
- `prior_quality_score`
- `quality_delta`
- `recent_rework_rate`
- `risk_status`
- `risk_score`
- `risk_level`
- `risk_drivers`
- `recommended_action`

## Team Feature Model

For each team, Module C calculates:

- `team_id`
- `work_type`
- `region`
- `manager_name`
- `active_contributors`
- `sampled_quality_events`
- `avg_quality_score`
- `gold_task_fail_rate`
- `reviewer_override_rate`
- `avg_peer_agreement_score`
- `rework_rate`
- `low_tenure_share`
- `high_risk_contributor_count`
- `medium_risk_contributor_count`
- `recent_quality_score`
- `prior_quality_score`
- `quality_delta`
- `quality_drift_flag`
- `team_risk_score`
- `team_risk_level`
- `risk_drivers`
- `recommended_manager_action`

## Deterministic Risk Scoring

Contributor risk score uses:

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

Team risk score uses:

```text
team_risk_score = avg_quality_gap
                + gold_task_fail_rate_penalty
                + reviewer_override_rate_penalty
                + rework_rate_penalty
                + high_risk_contributor_count_penalty
                + low_tenure_share_penalty
                + quality_drift_penalty
```

Risk levels are deterministic:

- `High quality risk`
- `Medium quality risk`
- `Low quality risk`
- `Insufficient sample`

## Quality Drift Status

Contributor quality status can be:

- `Stable`
- `Improving`
- `Declining`
- `Volatile`
- `Insufficient sample`

The recent window is the last 30 days relative to the latest available quality event. The prior window is the previous 30 days.

Rules:

- Declining: recent quality score is at least 4 points lower than prior quality score.
- Improving: recent quality score is at least 4 points higher than prior quality score.
- Volatile: reviewer override rate is high or peer agreement is low despite acceptable average score.
- Stable: quality and rework signals are within expected range.
- Insufficient sample: not enough sampled quality events.

## Action Mapping

Module C maps dominant risk drivers to action archetypes:

| Risk driver | Recommended action |
| --- | --- |
| Low gold task pass rate | Gold task review + targeted coaching |
| High reviewer override rate | Reviewer calibration + manager review |
| Low peer agreement | Calibration huddle |
| High rework rate | Workflow coaching + task instruction review |
| Quality drop in recent period | Manager coaching check-in |
| Low tenure + high complexity | Training module update + gradual ramp |
| Team-wide drift | Team calibration huddle |
| Work-type-wide drift | SOP review + quality sampling increase |
| High-quality contributor concentration risk | Cross-training / capacity planning |

## Streamlit Page

The sidebar page is:

```text
pages/3_Module_C_Workforce_Quality_Scorer.py
```

Sections:

1. Executive Workforce Quality Summary
2. Contributor Quality Risk Table
3. Team Quality Risk Table
4. Quality Drift View
5. Contributor / Team Drilldown
6. Weekly Coaching and Calibration Queue
7. Quality Coaching Card Generator
8. Module C Weekly Briefing

## Integration With Module A

Module A shows where regional health is degrading through work type, quality, rework, backlog, SLA, CSAT, and escalation signals.

Module C explains which teams, contributors, cohorts, or operating conditions may be driving the quality risk.

Example talk track:

> Module A shows code review quality degrading. Module C lets me inspect whether that degradation is concentrated in a team, new contributor cohort, high-complexity tasks, reviewer overrides, or peer-agreement breakdown.

## Integration With Module B

Module B shows whether escalations are recurring operating-system failures.

Module C explains whether recurring escalations are linked to workforce quality drift, reviewer calibration drift, low peer agreement, low-tenure contributors, or high-complexity tasks.

Example talk track:

> Module B shows recurring reviewer-misalignment escalations in RLHF evaluation. Module C lets me check whether the pattern is tied to reviewer calibration drift, low peer agreement, low-tenure contributors, or high-complexity tasks.

## Validation

Run:

```bash
python -m py_compile app.py src/*.py pages/*.py
python -m streamlit run app.py
```

Then open the sidebar page:

```text
3 Module C Workforce Quality Scorer
```

Confirm:

- Contributor quality-risk summary renders.
- Team quality-risk summary renders.
- Work-type quality-risk summary renders.
- Weekly coaching and calibration queue renders.
- Contributor drilldown works.
- Team drilldown works.
- Quality coaching cards render and download.
- Module C weekly briefing renders and downloads.

## Final Command-Center Story

> Module A shows where the operation is unhealthy. Module B shows whether escalations are recurring system failures. Module C shows whether distributed workforce quality risk is emerging and what coaching, calibration, or staffing action should happen next.
